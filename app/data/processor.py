"""
Advanced NetCDF Data Processing Pipeline for Indian Ocean ARGO Data
Handles parsing, validation, quality control, and feature extraction
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
import xarray as xr
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import requests
import aiohttp
import aiofiles

from ..core.database import db, ARGOProfile, DataProcessingLog
from ..core.vector_db import vector_db
from ..core.config import settings

logger = logging.getLogger(__name__)

class ARGONetCDFProcessor:
    """
    Advanced NetCDF processor for ARGO float data
    Handles parsing, validation, and quality control
    """
    
    def __init__(self):
        self.gdac_base_url = "https://data-argo.ifremer.fr"
        self.quality_flags_accept = settings.QC_FLAGS_ACCEPT
        self.indian_ocean_bounds = settings.INDIAN_OCEAN_BOUNDS
        
        # Create processing directories
        self.netcdf_dir = Path(settings.DATA_DIR) / "netcdf"
        self.processed_dir = Path(settings.DATA_DIR) / "processed"
        self.failed_dir = Path(settings.DATA_DIR) / "failed"
        
        for directory in [self.netcdf_dir, self.processed_dir, self.failed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def fetch_argo_index(self) -> pd.DataFrame:
        """Fetch and parse ARGO global index"""
        
        logger.info("Fetching ARGO global index...")
        
        try:
            index_url = f"{self.gdac_base_url}/ar_index_global_prof.txt.gz"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(index_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Parse compressed index
                        import gzip
                        import io
                        
                        decompressed = gzip.decompress(content)
                        
                        # Read as CSV, skipping header comments
                        index_df = pd.read_csv(
                            io.BytesIO(decompressed),
                            skiprows=8,
                            parse_dates=['date', 'date_update']
                        )
                        
                        logger.info(f"Loaded ARGO index with {len(index_df)} profiles")
                        return index_df
                    
                    else:
                        raise Exception(f"Failed to fetch index: HTTP {response.status}")
        
        except Exception as e:
            logger.error(f"Index fetching failed: {e}")
            return pd.DataFrame()
    
    def filter_indian_ocean_profiles(self, index_df: pd.DataFrame, 
                                   date_range: Tuple[str, str] = None,
                                   max_profiles: int = 1000) -> pd.DataFrame:
        """Filter profiles for Indian Ocean region"""
        
        if index_df.empty:
            return index_df
        
        logger.info("Filtering profiles for Indian Ocean...")
        
        bounds = self.indian_ocean_bounds
        
        # Geographic filtering
        indian_ocean_mask = (
            (index_df['latitude'] >= bounds["lat_min"]) &
            (index_df['latitude'] <= bounds["lat_max"]) &
            (index_df['longitude'] >= bounds["lon_min"]) &
            (index_df['longitude'] <= bounds["lon_max"])
        )
        
        filtered_df = index_df[indian_ocean_mask].copy()
        
        # Date filtering
        if date_range:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['date'] >= start_date) &
                (filtered_df['date'] <= end_date)
            ]
        else:
            # Default: recent 5 years
            recent_date = datetime.now() - timedelta(days=365*5)
            filtered_df = filtered_df[filtered_df['date'] >= recent_date]
        
        # Limit number of profiles
        if len(filtered_df) > max_profiles:
            # Sample randomly to get diverse coverage
            filtered_df = filtered_df.sample(n=max_profiles, random_state=42)
        
        # Add regional classification
        filtered_df['ocean_subregion'] = filtered_df.apply(
            lambda row: settings.classify_region(row['latitude'], row['longitude']), 
            axis=1
        )
        
        logger.info(f"Filtered to {len(filtered_df)} Indian Ocean profiles")
        return filtered_df.sort_values('date')
    
    async def download_netcdf_profiles(self, profile_list: pd.DataFrame, 
                                     max_concurrent: int = 10) -> List[str]:
        """Download NetCDF files asynchronously"""
        
        logger.info(f"Downloading {len(profile_list)} NetCDF files...")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        downloaded_files = []
        
        async def download_single_profile(session: aiohttp.ClientSession, 
                                        profile_info: Dict) -> Optional[str]:
            async with semaphore:
                try:
                    file_url = f"{self.gdac_base_url}/{profile_info['file']}"
                    file_name = Path(profile_info['file']).name
                    local_path = self.netcdf_dir / file_name
                    
                    # Skip if already downloaded
                    if local_path.exists() and local_path.stat().st_size > 1000:
                        return str(local_path)
                    
                    async with session.get(file_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            async with aiofiles.open(local_path, 'wb') as f:
                                await f.write(content)
                            
                            logger.debug(f"Downloaded: {file_name}")
                            return str(local_path)
                        else:
                            logger.warning(f"Download failed: {file_url} (HTTP {response.status})")
                            return None
                
                except Exception as e:
                    logger.error(f"Download error for {profile_info.get('file', 'unknown')}: {e}")
                    return None
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            
            tasks = [
                download_single_profile(session, profile_info)
                for profile_info in profile_list.to_dict('records')
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful downloads
            downloaded_files = [
                result for result in results 
                if isinstance(result, str) and result is not None
            ]
        
        logger.info(f"Successfully downloaded {len(downloaded_files)} files")
        return downloaded_files
    
    def parse_netcdf_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse single NetCDF file and extract oceanographic data"""
        
        try:
            with xr.open_dataset(file_path) as dataset:
                
                # Validate dataset structure
                if not self.validate_netcdf_structure(dataset):
                    logger.warning(f"Invalid NetCDF structure: {file_path}")
                    return None
                
                # Extract basic profile information
                profile_data = self.extract_basic_profile_info(dataset, file_path)
                
                if not profile_data:
                    return None
                
                # Extract measurement data with QC
                measurements = self.extract_measurements_with_qc(dataset)
                profile_data.update(measurements)
                
                # Calculate derived parameters
                derived_params = self.calculate_derived_parameters(dataset, measurements)
                profile_data.update(derived_params)
                
                # Generate scientific summary
                profile_data['profile_summary'] = self.generate_profile_summary(
                    profile_data, measurements
                )
                
                profile_data['scientific_summary'] = self.generate_scientific_summary(
                    profile_data, measurements
                )
                
                # Add regional context
                profile_data['ocean_region'] = settings.classify_region(
                    profile_data['latitude'], 
                    profile_data['longitude']
                )
                
                return profile_data
                
        except Exception as e:
            logger.error(f"NetCDF parsing failed for {file_path}: {e}")
            return None
    
    def validate_netcdf_structure(self, dataset: xr.Dataset) -> bool:
        """Validate NetCDF file structure and required variables"""
        
        required_vars = ['TEMP', 'PSAL', 'PRES', 'LATITUDE', 'LONGITUDE', 'JULD']
        required_qc_vars = ['TEMP_QC', 'PSAL_QC', 'PRES_QC']
        
        # Check for required variables
        for var in required_vars:
            if var not in dataset.variables:
                logger.debug(f"Missing required variable: {var}")
                return False
        
        # Check for QC variables (optional but preferred)
        qc_count = sum(1 for var in required_qc_vars if var in dataset.variables)
        
        if qc_count == 0:
            logger.warning("No QC variables found - data quality assessment limited")
        
        # Check data dimensions
        if 'N_LEVELS' not in dataset.dims:
            logger.debug("Missing N_LEVELS dimension")
            return False
        
        # Check for minimum data
        if dataset.dims['N_LEVELS'] < 3:
            logger.debug("Insufficient vertical levels")
            return False
        
        return True
    
    def extract_basic_profile_info(self, dataset: xr.Dataset, file_path: str) -> Optional[Dict]:
        """Extract basic profile metadata"""
        
        try:
            # Extract scalar variables
            profile_data = {
                'id': self.generate_profile_uuid(),
                'float_id': str(dataset.attrs.get('platform_number', '')).strip(),
                'cycle_number': int(dataset.CYCLE_NUMBER.values[0]) if 'CYCLE_NUMBER' in dataset else None,
                'source_file': Path(file_path).name,
                'processed_date': datetime.utcnow()
            }
            
            # Extract coordinates
            profile_data['latitude'] = float(dataset.LATITUDE.values[0])
            profile_data['longitude'] = float(dataset.LONGITUDE.values[0])
            
            # Validate coordinates
            if not self.validate_coordinates(profile_data['latitude'], profile_data['longitude']):
                logger.warning(f"Invalid coordinates: {profile_data['latitude']}, {profile_data['longitude']}")
                return None
            
            # Extract date
            juld = dataset.JULD.values[0]
            if pd.isna(juld):
                logger.warning("Invalid profile date")
                return None
            
            # Convert JULD (days since 1950-01-01) to datetime
            reference_date = pd.Timestamp('1950-01-01')
            profile_data['profile_date'] = reference_date + pd.Timedelta(days=float(juld))
            
            # Extract metadata
            profile_data['data_source'] = 'argo_gdac'
            profile_data['platform_type'] = dataset.attrs.get('platform_type', 'ARGO_FLOAT')
            profile_data['processing_level'] = self.determine_processing_level(dataset)
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Basic info extraction failed: {e}")
            return None
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate geographic coordinates"""
        
        if not (-90 <= lat <= 90):
            return False
        
        if not (-180 <= lon <= 180):
            return False
        
        # Check if within Indian Ocean bounds (with buffer)
        bounds = self.indian_ocean_bounds
        buffer = 5.0  # degrees
        
        return (
            (bounds["lat_min"] - buffer) <= lat <= (bounds["lat_max"] + buffer) and
            (bounds["lon_min"] - buffer) <= lon <= (bounds["lon_max"] + buffer)
        )
    
    def determine_processing_level(self, dataset: xr.Dataset) -> str:
        """Determine data processing level"""
        
        # Check for delayed mode indicators
        if 'DATA_MODE' in dataset.variables:
            data_mode = dataset.DATA_MODE.values[0]
            if isinstance(data_mode, bytes):
                data_mode = data_mode.decode('utf-8').strip()
            
            if data_mode == 'D':
                return 'delayed_mode'
            elif data_mode == 'A':
                return 'adjusted'
            else:
                return 'real_time'
        
        # Fallback based on QC variables
        qc_vars = ['TEMP_ADJUSTED_QC', 'PSAL_ADJUSTED_QC']
        has_adjusted = any(var in dataset.variables for var in qc_vars)
        
        return 'delayed_mode' if has_adjusted else 'real_time'
    
    def extract_measurements_with_qc(self, dataset: xr.Dataset) -> Dict[str, Any]:
        """Extract oceanographic measurements with quality control"""
        
        measurements = {}
        
        try:
            # Temperature data
            temp_data, temp_qc = self.extract_parameter_with_qc(
                dataset, 'TEMP', 'TEMP_QC'
            )
            
            if temp_data is not None:
                measurements.update({
                    'surface_temperature': temp_data[0] if len(temp_data) > 0 else None,
                    'temperature_profile': temp_data.tolist() if len(temp_data) < 200 else temp_data[:200].tolist(),
                    'temperature_qc_flags': temp_qc.tolist() if temp_qc is not None else None,
                    'has_temperature': True
                })
                
                # Temperature statistics
                valid_temps = temp_data[~np.isnan(temp_data)]
                if len(valid_temps) > 0:
                    measurements.update({
                        'temp_mean': float(np.mean(valid_temps)),
                        'temp_std': float(np.std(valid_temps)),
                        'temperature_range': float(np.max(valid_temps) - np.min(valid_temps))
                    })
            else:
                measurements['has_temperature'] = False
            
            # Salinity data
            sal_data, sal_qc = self.extract_parameter_with_qc(
                dataset, 'PSAL', 'PSAL_QC'
            )
            
            if sal_data is not None:
                measurements.update({
                    'surface_salinity': sal_data[0] if len(sal_data) > 0 else None,
                    'salinity_profile': sal_data.tolist() if len(sal_data) < 200 else sal_data[:200].tolist(),
                    'salinity_qc_flags': sal_qc.tolist() if sal_qc is not None else None,
                    'has_salinity': True
                })
                
                # Salinity statistics
                valid_sals = sal_data[~np.isnan(sal_data)]
                if len(valid_sals) > 0:
                    measurements.update({
                        'salinity_mean': float(np.mean(valid_sals)),
                        'salinity_std': float(np.std(valid_sals)),
                        'salinity_range': float(np.max(valid_sals) - np.min(valid_sals))
                    })
            else:
                measurements['has_salinity'] = False
            
            # Pressure data
            pres_data, pres_qc = self.extract_parameter_with_qc(
                dataset, 'PRES', 'PRES_QC'
            )
            
            if pres_data is not None:
                measurements.update({
                    'surface_pressure': pres_data[0] if len(pres_data) > 0 else None,
                    'pressure_profile': pres_data.tolist() if len(pres_data) < 200 else pres_data[:200].tolist(),
                    'max_depth': float(np.nanmax(pres_data)),
                    'num_levels': len(pres_data[~np.isnan(pres_data)]),
                    'has_pressure': True
                })
            else:
                measurements['has_pressure'] = False
            
            # Additional parameters (if available)
            additional_params = {
                'DOXY': 'oxygen',
                'CHLA': 'chlorophyll',
                'BBP700': 'backscatter',
                'PH_IN_SITU_TOTAL': 'ph',
                'NITRATE': 'nitrate'
            }
            
            for netcdf_var, param_name in additional_params.items():
                if netcdf_var in dataset.variables:
                    param_data, _ = self.extract_parameter_with_qc(dataset, netcdf_var)
                    if param_data is not None:
                        measurements[f'has_{param_name}'] = True
                        measurements[f'surface_{param_name}'] = param_data[0] if len(param_data) > 0 else None
                    else:
                        measurements[f'has_{param_name}'] = False
                else:
                    measurements[f'has_{param_name}'] = False
            
            return measurements
            
        except Exception as e:
            logger.error(f"Measurement extraction failed: {e}")
            return {}
    
    def extract_parameter_with_qc(self, dataset: xr.Dataset, 
                                param_name: str, qc_name: str = None) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Extract parameter data with quality control filtering"""
        
        if param_name not in dataset.variables:
            return None, None
        
        try:
            # Get data
            data = dataset[param_name].values.flatten()
            
            # Get QC flags if available
            qc_flags = None
            if qc_name and qc_name in dataset.variables:
                qc_flags = dataset[qc_name].values.flatten()
                
                # Convert QC flags to numeric if they're strings/bytes
                if qc_flags.dtype.kind in ['U', 'S', 'O']:
                    qc_numeric = []
                    for flag in qc_flags:
                        if isinstance(flag, bytes):
                            flag = flag.decode('utf-8')
                        try:
                            qc_numeric.append(int(str(flag).strip()))
                        except (ValueError, AttributeError):
                            qc_numeric.append(9)  # Unknown/bad quality
                    qc_flags = np.array(qc_numeric)
                
                # Filter data based on acceptable QC flags
                if len(qc_flags) == len(data):
                    acceptable_mask = np.isin(qc_flags, self.quality_flags_accept)
                    data = np.where(acceptable_mask, data, np.nan)
            
            # Remove fill values
            if hasattr(dataset[param_name], '_FillValue'):
                fill_value = dataset[param_name]._FillValue
                data = np.where(data == fill_value, np.nan, data)
            
            # Remove unrealistic values based on parameter type
            data = self.filter_unrealistic_values(param_name, data)
            
            return data, qc_flags
            
        except Exception as e:
            logger.error(f"Parameter extraction failed for {param_name}: {e}")
            return None, None
    
    def filter_unrealistic_values(self, param_name: str, data: np.ndarray) -> np.ndarray:
        """Filter unrealistic values based on oceanographic ranges"""
        
        realistic_ranges = {
            'TEMP': (-3.0, 40.0),      # Temperature in °C
            'PSAL': (0.0, 45.0),       # Salinity in PSU
            'PRES': (0.0, 12000.0),    # Pressure in dbar
            'DOXY': (0.0, 600.0),      # Oxygen in µmol/kg
            'PH_IN_SITU_TOTAL': (6.0, 9.0),  # pH
            'NITRATE': (0.0, 100.0),   # Nitrate in µmol/kg
            'CHLA': (0.0, 100.0)       # Chlorophyll in mg/m³
        }
        
        if param_name in realistic_ranges:
            min_val, max_val = realistic_ranges[param_name]
            data = np.where((data >= min_val) & (data <= max_val), data, np.nan)
        
        return data
    
    def calculate_derived_parameters(self, dataset: xr.Dataset, 
                                   measurements: Dict) -> Dict[str, Any]:
        """Calculate derived oceanographic parameters"""
        
        derived = {}
        
        try:
            # Mixed Layer Depth calculation
            if measurements.get('has_temperature') and measurements.get('has_pressure'):
                temp_profile = np.array(measurements.get('temperature_profile', []))
                pres_profile = np.array(measurements.get('pressure_profile', []))
                
                if len(temp_profile) > 10 and len(pres_profile) > 10:
                    mld = self.calculate_mixed_layer_depth(temp_profile, pres_profile)
                    derived['mixed_layer_depth'] = mld
            
            # Thermocline depth
            if measurements.get('has_temperature') and measurements.get('has_pressure'):
                thermocline_depth = self.calculate_thermocline_depth(
                    measurements.get('temperature_profile', []),
                    measurements.get('pressure_profile', [])
                )
                derived['thermocline_depth'] = thermocline_depth
            
            # Halocline depth (if salinity available)
            if measurements.get('has_salinity') and measurements.get('has_pressure'):
                halocline_depth = self.calculate_halocline_depth(
                    measurements.get('salinity_profile', []),
                    measurements.get('pressure_profile', [])
                )
                derived['halocline_depth'] = halocline_depth
            
            # Surface density (if T and S available)
            if (measurements.get('surface_temperature') and 
                measurements.get('surface_salinity')):
                
                surf_density = self.calculate_seawater_density(
                    measurements['surface_temperature'],
                    measurements['surface_salinity'],
                    measurements.get('surface_pressure', 0)
                )
                derived['surface_density'] = surf_density
            
            # Data quality score
            derived['data_quality_score'] = self.calculate_data_quality_score(
                dataset, measurements
            )
            
            # Position accuracy assessment
            derived['position_accuracy'] = self.assess_position_accuracy(dataset)
            
            # Time accuracy assessment  
            derived['time_accuracy'] = self.assess_time_accuracy(dataset)
            
            return derived
            
        except Exception as e:
            logger.error(f"Derived parameter calculation failed: {e}")
            return {}
    
    def calculate_mixed_layer_depth(self, temp_profile: np.ndarray, 
                                  pres_profile: np.ndarray, 
                                  threshold: float = 0.2) -> Optional[float]:
        """Calculate mixed layer depth using temperature criterion"""
        
        try:
            # Remove NaN values
            valid_mask = ~(np.isnan(temp_profile) | np.isnan(pres_profile))
            temp = temp_profile[valid_mask]
            pres = pres_profile[valid_mask]
            
            if len(temp) < 5 or len(pres) < 5:
                return None
            
            # Sort by pressure (depth)
            sorted_indices = np.argsort(pres)
            temp = temp[sorted_indices]
            pres = pres[sorted_indices]
            
            # Find surface temperature (shallowest measurement)
            surf_temp = temp[0]
            
            # Find first depth where temperature differs by threshold
            temp_diff = np.abs(temp - surf_temp)
            mld_indices = np.where(temp_diff >= threshold)[0]
            
            if len(mld_indices) > 0:
                mld = float(pres[mld_indices[0]])
                return mld if mld > 0 else None
            
            return None
            
        except Exception as e:
            logger.debug(f"MLD calculation failed: {e}")
            return None
    
    def calculate_thermocline_depth(self, temp_profile: List, 
                                  pres_profile: List) -> Optional[float]:
        """Calculate thermocline depth (maximum temperature gradient)"""
        
        try:
            temp = np.array(temp_profile)
            pres = np.array(pres_profile)
            
            # Remove NaN values
            valid_mask = ~(np.isnan(temp) | np.isnan(pres))
            temp = temp[valid_mask]
            pres = pres[valid_mask]
            
            if len(temp) < 10:
                return None
            
            # Sort by pressure
            sorted_indices = np.argsort(pres)
            temp = temp[sorted_indices]
            pres = pres[sorted_indices]
            
            # Calculate temperature gradient
            dt_dp = np.gradient(temp, pres)
            
            # Find maximum gradient (steepest thermocline)
            max_gradient_idx = np.argmax(np.abs(dt_dp))
            
            thermocline_depth = float(pres[max_gradient_idx])
            
            # Validate thermocline depth (should be below surface)
            return thermocline_depth if thermocline_depth > 10 else None
            
        except Exception as e:
            logger.debug(f"Thermocline calculation failed: {e}")
            return None
    
    def calculate_halocline_depth(self, sal_profile: List, 
                                pres_profile: List) -> Optional[float]:
        """Calculate halocline depth (maximum salinity gradient)"""
        
        try:
            sal = np.array(sal_profile)
            pres = np.array(pres_profile)
            
            # Remove NaN values
            valid_mask = ~(np.isnan(sal) | np.isnan(pres))
            sal = sal[valid_mask]
            pres = pres[valid_mask]
            
            if len(sal) < 10:
                return None
            
            # Sort by pressure
            sorted_indices = np.argsort(pres)
            sal = sal[sorted_indices]
            pres = pres[sorted_indices]
            
            # Calculate salinity gradient
            ds_dp = np.gradient(sal, pres)
            
            # Find maximum gradient
            max_gradient_idx = np.argmax(np.abs(ds_dp))
            
            halocline_depth = float(pres[max_gradient_idx])
            
            return halocline_depth if halocline_depth > 5 else None
            
        except Exception as e:
            logger.debug(f"Halocline calculation failed: {e}")
            return None
    
    def calculate_seawater_density(self, temp: float, sal: float, 
                                 pres: float = 0) -> Optional[float]:
        """Calculate seawater density using simplified equation of state"""
        
        try:
            # Simplified UNESCO equation of state for seawater density
            # This is a basic approximation - for research use a proper library like gsw
            
            # Convert pressure from dbar to bar
            p_bar = pres * 0.1
            
            # Density at atmospheric pressure
            rho0 = (999.842594 + 
                   6.793952e-2 * temp - 
                   9.095290e-3 * temp**2 + 
                   1.001685e-4 * temp**3 - 
                   1.120083e-6 * temp**4 + 
                   6.536332e-9 * temp**5)
            
            # Salinity effect
            rho = (rho0 + 
                  sal * (0.824493 - 4.0899e-3 * temp + 
                        7.6438e-5 * temp**2 - 8.2467e-7 * temp**3 + 
                        5.3875e-9 * temp**4) +
                  sal**1.5 * (-5.72466e-3 + 1.0227e-4 * temp - 
                             1.6546e-6 * temp**2) +
                  sal**2 * 4.8314e-4)
            
            # Pressure correction (simplified)
            rho_p = rho * (1 + p_bar * 4.5e-6)
            
            return float(rho_p) if 900 < rho_p < 1100 else None
            
        except Exception as e:
            logger.debug(f"Density calculation failed: {e}")
            return None
    
    def calculate_data_quality_score(self, dataset: xr.Dataset, 
                                   measurements: Dict) -> float:
        """Calculate overall data quality score (1-5 scale)"""
        
        score = 5.0  # Start with perfect score
        
        try:
            # Penalize for missing core parameters
            if not measurements.get('has_temperature', False):
                score -= 1.5
            if not measurements.get('has_salinity', False):
                score -= 1.5
            if not measurements.get('has_pressure', False):
                score -= 1.0
            
            # Quality based on number of levels
            num_levels = measurements.get('num_levels', 0)
            if num_levels < 10:
                score -= 1.0
            elif num_levels < 50:
                score -= 0.5
            
            # Quality based on QC flags (if available)
            temp_qc = measurements.get('temperature_qc_flags', [])
            sal_qc = measurements.get('salinity_qc_flags', [])
            
            if temp_qc:
                good_temp_ratio = sum(1 for qc in temp_qc if qc in [1, 2]) / len(temp_qc)
                score -= (1 - good_temp_ratio) * 0.5
            
            if sal_qc:
                good_sal_ratio = sum(1 for qc in sal_qc if qc in [1, 2]) / len(sal_qc)
                score -= (1 - good_sal_ratio) * 0.5
            
            # Processing level bonus
            processing_level = self.determine_processing_level(dataset)
            if processing_level == 'delayed_mode':
                score += 0.2
            elif processing_level == 'adjusted':
                score += 0.1
            
            # Ensure score is within bounds
            return max(1.0, min(5.0, score))
            
        except Exception as e:
            logger.debug(f"Quality score calculation failed: {e}")
            return 3.0  # Default moderate quality
    
    def assess_position_accuracy(self, dataset: xr.Dataset) -> str:
        """Assess position accuracy based on available metadata"""
        
        try:
            # Check for position accuracy indicators
            if 'POSITION_QC' in dataset.variables:
                pos_qc = dataset.POSITION_QC.values[0]
                if isinstance(pos_qc, bytes):
                    pos_qc = int(pos_qc.decode('utf-8').strip())
                
                if pos_qc in [1, 2]:
                    return 'high'
                elif pos_qc in [3, 4]:
                    return 'standard'
                else:
                    return 'low'
            
            # Fallback based on processing level
            processing_level = self.determine_processing_level(dataset)
            if processing_level == 'delayed_mode':
                return 'high'
            else:
                return 'standard'
                
        except Exception as e:
            logger.debug(f"Position accuracy assessment failed: {e}")
            return 'standard'
    
    def assess_time_accuracy(self, dataset: xr.Dataset) -> str:
        """Assess time accuracy based on available metadata"""
        
        try:
            # Check for time QC indicators
            if 'JULD_QC' in dataset.variables:
                time_qc = dataset.JULD_QC.values[0]
                if isinstance(time_qc, bytes):
                    time_qc = int(time_qc.decode('utf-8').strip())
                
                if time_qc in [1, 2]:
                    return 'high'
                elif time_qc in [3, 4]:
                    return 'standard'
                else:
                    return 'low'
            
            return 'standard'
            
        except Exception as e:
            logger.debug(f"Time accuracy assessment failed: {e}")
            return 'standard'
    
    def generate_profile_summary(self, profile_data: Dict, 
                               measurements: Dict) -> str:
        """Generate human-readable profile summary"""
        
        try:
            region = profile_data.get('ocean_region', 'Indian Ocean')
            date = profile_data.get('profile_date', datetime.now())
            
            # Format region name
            region_names = {
                'arabian_sea': 'Arabian Sea',
                'bay_of_bengal': 'Bay of Bengal', 
                'equatorial_indian': 'Equatorial Indian Ocean'
            }
            region_display = region_names.get(region, region.replace('_', ' ').title())
            
            # Basic info
            summary = f"ARGO profile from {region_display} collected on {date.strftime('%Y-%m-%d')}"
            
            # Add measurement details
            details = []
            
            if measurements.get('surface_temperature'):
                temp = measurements['surface_temperature']
                details.append(f"surface temperature {temp:.1f}°C")
            
            if measurements.get('surface_salinity'):
                sal = measurements['surface_salinity']
                details.append(f"salinity {sal:.1f} PSU")
            
            if measurements.get('max_depth'):
                depth = measurements['max_depth']
                details.append(f"max depth {depth:.0f}m")
            
            if details:
                summary += f" with {', '.join(details)}"
            
            # Add quality indicator
            quality_score = profile_data.get('data_quality_score', 3.0)
            if quality_score >= 4.5:
                summary += ". Excellent data quality."
            elif quality_score >= 4.0:
                summary += ". High data quality."
            elif quality_score >= 3.0:
                summary += ". Good data quality."
            else:
                summary += ". Standard data quality."
            
            return summary
            
        except Exception as e:
            logger.debug(f"Profile summary generation failed: {e}")
            return f"ARGO profile from {profile_data.get('ocean_region', 'Indian Ocean')}"
    
    def generate_scientific_summary(self, profile_data: Dict, 
                                  measurements: Dict) -> str:
        """Generate scientific summary with oceanographic context"""
        
        try:
            region = profile_data.get('ocean_region', 'indian_ocean_general')
            lat = profile_data.get('latitude', 0)
            lon = profile_data.get('longitude', 0)
            date = profile_data.get('profile_date', datetime.now())
            
            # Get seasonal context
            season_context = settings.get_seasonal_context(date.month)
            season_name = season_context.get('description', 'Unknown season')
            
            # Regional context
            regional_context = settings.get_regional_context(region)
            region_name = regional_context.get('full_name', 'Indian Ocean')
            
            # Build scientific summary
            summary = f"Oceanographic profile from {region_name} ({lat:.2f}°N, {lon:.2f}°E) during {season_name}"
            
            # Add scientific measurements context
            scientific_details = []
            
            if measurements.get('surface_temperature'):
                temp = measurements['surface_temperature']
                temp_range = regional_context.get('typical_temp_range', 'variable')
                scientific_details.append(f"SST {temp:.2f}°C (typical range: {temp_range})")
            
            if measurements.get('surface_salinity'):
                sal = measurements['surface_salinity']
                sal_range = regional_context.get('typical_salinity_range', 'variable')
                scientific_details.append(f"SSS {sal:.2f} PSU (typical range: {sal_range})")
            
            if measurements.get('mixed_layer_depth'):
                mld = measurements['mixed_layer_depth']
                scientific_details.append(f"MLD {mld:.0f}m")
            
            if scientific_details:
                summary += f". Key parameters: {'; '.join(scientific_details)}"
            
            # Add regional phenomena context
            phenomena = regional_context.get('key_phenomena', [])
            if phenomena:
                summary += f". Influenced by {', '.join(phenomena[:2])}"
            
            # Add seasonal characteristics
            season_chars = season_context.get('characteristics', '')
            if season_chars:
                summary += f". Seasonal characteristics: {season_chars.lower()}"
            
            return summary
            
        except Exception as e:
            logger.debug(f"Scientific summary generation failed: {e}")
            return f"Oceanographic profile from Indian Ocean region"
    
    def generate_profile_uuid(self) -> str:
        """Generate unique profile identifier"""
        import uuid
        return str(uuid.uuid4())
    
    async def process_netcdf_batch(self, file_paths: List[str], 
                                 max_workers: int = 4) -> Dict[str, Any]:
        """Process multiple NetCDF files concurrently"""
        
        logger.info(f"Processing {len(file_paths)} NetCDF files...")
        
        processing_start = datetime.utcnow()
        successful_profiles = []
        failed_files = []
        
        # Process files in parallel using ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            
            # Submit all parsing tasks
            future_to_file = {
                executor.submit(self.parse_netcdf_file, file_path): file_path
                for file_path in file_paths
            }
            
            # Collect results
            for future in future_to_file:
                file_path = future_to_file[future]
                
                try:
                    profile_data = future.result(timeout=30)
                    
                    if profile_data:
                        successful_profiles.append(profile_data)
                        logger.debug(f"Successfully processed: {Path(file_path).name}")
                    else:
                        failed_files.append(file_path)
                        logger.warning(f"Failed to parse: {Path(file_path).name}")
                        
                except Exception as e:
                    failed_files.append(file_path)
                    logger.error(f"Processing error for {Path(file_path).name}: {e}")
        
        processing_time = (datetime.utcnow() - processing_start).total_seconds()
        
        # Log processing summary
        logger.info(f"NetCDF processing completed:")
        logger.info(f"  Successful: {len(successful_profiles)}")
        logger.info(f"  Failed: {len(failed_files)}")
        logger.info(f"  Processing time: {processing_time:.2f}s")
        
        return {
            'successful_profiles': successful_profiles,
            'failed_files': failed_files,
            'processing_time_seconds': processing_time,
            'success_rate': len(successful_profiles) / len(file_paths) if file_paths else 0
        }
    
    async def store_profiles_in_database(self, profiles: List[Dict]) -> Dict[str, Any]:
        """Store processed profiles in PostgreSQL database"""
        
        logger.info(f"Storing {len(profiles)} profiles in database...")
        
        storage_start = datetime.utcnow()
        stored_count = 0
        errors = []
        
        try:
            with db.get_session() as session:
                
                for profile_data in profiles:
                    try:
                        # Create ARGO profile object
                        argo_profile = ARGOProfile(**profile_data)
                        
                        # Check for duplicates
                        existing = session.query(ARGOProfile).filter(
                            ARGOProfile.float_id == profile_data['float_id'],
                            ARGOProfile.cycle_number == profile_data['cycle_number']
                        ).first()
                        
                        if existing:
                            logger.debug(f"Skipping duplicate profile: {profile_data['float_id']}-{profile_data['cycle_number']}")
                            continue
                        
                        session.add(argo_profile)
                        stored_count += 1
                        
                    except Exception as e:
                        error_msg = f"Failed to store profile {profile_data.get('float_id', 'unknown')}: {e}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
                # Commit all profiles
                session.commit()
                
        except Exception as e:
            logger.error(f"Database storage failed: {e}")
            return {
                'stored_count': 0,
                'errors': [str(e)],
                'storage_time_seconds': 0
            }
        
        storage_time = (datetime.utcnow() - storage_start).total_seconds()
        
        logger.info(f"Database storage completed: {stored_count} profiles stored")
        
        return {
            'stored_count': stored_count,
            'errors': errors,
            'storage_time_seconds': storage_time
        }
    
    async def generate_embeddings_for_profiles(self, profiles: List[Dict]) -> Dict[str, Any]:
        """Generate vector embeddings for profiles"""
        
        logger.info(f"Generating embeddings for {len(profiles)} profiles...")
        
        embedding_start = datetime.utcnow()
        
        try:
            # Create ARGOProfile objects for vector DB
            argo_profiles = []
            
            for profile_data in profiles:
                try:
                    argo_profile = ARGOProfile(**profile_data)
                    argo_profiles.append(argo_profile)
                except Exception as e:
                    logger.warning(f"Failed to create profile object for embedding: {e}")
            
            # Generate embeddings using vector database
            embedding_results = vector_db.add_profiles_advanced(argo_profiles)
            
            embedding_time = (datetime.utcnow() - embedding_start).total_seconds()
            
            logger.info(f"Embedding generation completed in {embedding_time:.2f}s")
            
            return {
                'embeddings_generated': embedding_results.get('profiles_added', 0),
                'embedding_time_seconds': embedding_time,
                'embedding_errors': embedding_results.get('errors', [])
            }
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {
                'embeddings_generated': 0,
                'embedding_time_seconds': 0,
                'embedding_errors': [str(e)]
            }
    
    async def log_processing_operation(self, operation_results: Dict) -> None:
        """Log processing operation in database"""
        
        try:
            with db.get_session() as session:
                
                log_entry = DataProcessingLog(
                    operation_type='netcdf_processing',
                    operation_subtype='batch_ingestion',
                    operation_status='success' if operation_results.get('success_rate', 0) > 0.8 else 'partial_success',
                    records_processed=operation_results.get('total_files', 0),
                    records_accepted=operation_results.get('stored_count', 0),
                    records_rejected=operation_results.get('failed_count', 0),
                    processing_time_seconds=operation_results.get('total_time_seconds', 0),
                    processing_parameters=json.dumps({
                        'indian_ocean_focus': True,
                        'quality_threshold': settings.DATA_QUALITY_THRESHOLD,
                        'date_range': operation_results.get('date_range'),
                        'max_profiles': operation_results.get('max_profiles')
                    }),
                    system_info=json.dumps(settings.get_system_info())
                )
                
                session.add(log_entry)
                session.commit()
                
                logger.info("Processing operation logged successfully")
                
        except Exception as e:
            logger.error(f"Failed to log processing operation: {e}")
    
    async def run_complete_ingestion_pipeline(self, 
                                            date_range: Tuple[str, str] = None,
                                            max_profiles: int = 1000) -> Dict[str, Any]:
        """Run complete ARGO data ingestion pipeline"""
        
        pipeline_start = datetime.utcnow()
        
        logger.info("Starting complete ARGO data ingestion pipeline...")
        logger.info(f"Target: {max_profiles} profiles from Indian Ocean")
        
        try:
            # Step 1: Fetch ARGO index
            index_df = await self.fetch_argo_index()
            if index_df.empty:
                raise Exception("Failed to fetch ARGO index")
            
            # Step 2: Filter for Indian Ocean profiles
            filtered_profiles = self.filter_indian_ocean_profiles(
                index_df, date_range, max_profiles
            )
            
            if filtered_profiles.empty:
                raise Exception("No Indian Ocean profiles found in index")
            
            # Step 3: Download NetCDF files
            downloaded_files = await self.download_netcdf_profiles(filtered_profiles)
            
            if not downloaded_files:
                raise Exception("No NetCDF files downloaded successfully")
            
            # Step 4: Process NetCDF files
            processing_results = await self.process_netcdf_batch(downloaded_files)
            
            successful_profiles = processing_results.get('successful_profiles', [])
            
            if not successful_profiles:
                raise Exception("No profiles processed successfully")
            
            # Step 5: Store profiles in database
            storage_results = await self.store_profiles_in_database(successful_profiles)
            
            # Step 6: Generate embeddings
            embedding_results = await self.generate_embeddings_for_profiles(successful_profiles)
            
            # Calculate overall results
            total_time = (datetime.utcnow() - pipeline_start).total_seconds()
            
            operation_results = {
                'total_files': len(downloaded_files),
                'successful_profiles': len(successful_profiles),
                'stored_count': storage_results.get('stored_count', 0),
                'failed_count': len(processing_results.get('failed_files', [])),
                'success_rate': processing_results.get('success_rate', 0),
                'total_time_seconds': total_time,
                'date_range': date_range,
                'max_profiles': max_profiles,
                'embeddings_generated': embedding_results.get('embeddings_generated', 0)
            }
            
            # Log the operation
            await self.log_processing_operation(operation_results)
            
            logger.info("ARGO ingestion pipeline completed successfully")
            logger.info(f"Total time: {total_time:.2f}s")
            logger.info(f"Profiles processed: {len(successful_profiles)}")
            logger.info(f"Profiles stored: {storage_results.get('stored_count', 0)}")
            
            return operation_results
            
        except Exception as e:
            total_time = (datetime.utcnow() - pipeline_start).total_seconds()
            logger.error(f"ARGO ingestion pipeline failed: {e}")
            
            # Log failed operation
            error_results = {
                'total_files': 0,
                'successful_profiles': 0,
                'stored_count': 0,
                'failed_count': 0,
                'success_rate': 0,
                'total_time_seconds': total_time,
                'error': str(e)
            }
            
            await self.log_processing_operation(error_results)
            
            return error_results

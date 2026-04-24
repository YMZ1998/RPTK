#!/usr/bin/env python3
"""
RPTK启动脚本 - 设置正确的sys.path
"""
import sys
from pathlib import Path

# 添加项目根目录到sys.path，让mirp和src模块可被导入
RPTK_ROOT = Path(__file__).parent.resolve()
if str(RPTK_ROOT) not in sys.path:
    sys.path.insert(0, str(RPTK_ROOT))

# 现在运行原始的rptk-run.py
if __name__ == "__main__":
    import argparse
    import logging
    from typing import List, Union
    import pandas as pd
    from pandas.api.types import is_numeric_dtype
    
    # 直接导入RPTK类（现在路径已设置）
    from rptk import RPTK
    
    def best_or_int(value: str) -> Union[int, str]:
        v = value.strip().lower()
        if v == "best":
            return "best"
        try:
            i = int(v)
            if i <= 0:
                raise argparse.ArgumentTypeError("--n-features must be a positive integer or 'best'")
            return i
        except ValueError as e:
            raise argparse.ArgumentTypeError("--n-features must be an integer or 'best'") from e
    
    def build_parser() -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(
            description="RPTK - Radiomics Processing Toolkit"
        )
        
        # Input/Output
        p.add_argument("--input-csv", required=True, help="Path to input CSV file")
        p.add_argument("--output-dir", required=True, help="Output directory")
        
        # Processing options
        p.add_argument("--task", choices=["classification", "regression"], default="classification")
        p.add_argument("--n-features", type=best_or_int, default="best")
        p.add_argument("--random-state", type=int, default=42)
        
        # Feature extraction
        p.add_argument("--extractor", choices=["pyradiomics", "mirp", "both"], default="pyradiomics")
        
        # Model selection
        p.add_argument("--models", nargs="+", 
                       choices=["rf", "svm", "lr", "xgb", "lgbm", "tabnet"],
                       default=["rf", "svm", "lr"])
        
        # Parallel processing
        p.add_argument("--n-jobs", type=int, default=-1)
        
        # Logging
        p.add_argument("--verbose", action="store_true")
        p.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
        
        return p
    
    def main():
        parser = build_parser()
        args = parser.parse_args()
        
        # Setup logging
        level = getattr(logging, args.log_level)
        logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger = logging.getLogger("RPTK")
        
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        
        # Initialize RPTK
        rptk = RPTK(
            input_csv=args.input_csv,
            output_dir=args.output_dir,
            task=args.task,
            n_features=args.n_features,
            random_state=args.random_state,
            extractor=args.extractor,
            models=args.models,
            n_jobs=args.n_jobs,
            logger=logger
        )
        
        # Run pipeline
        rptk.run()
        
        logger.info(f"RPTK completed. Results saved to {args.output_dir}")
    
    main()
import os
import sys
import logging
from typing import Any
import duckdb

# Get current file's directory, go up 2 levels to 'pipeline'
current_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_root = os.path.dirname(current_dir)
project_root = os.path.dirname(pipeline_root)

sys.path.append(pipeline_root)

from config import load_config # noqa: E402

# Load config
config: dict[str, Any] = load_config()
log_level: str = getattr(logging, config["settings"]["log_level"])
export_logs: bool = config["settings"]["export_logs"]

# Conditional debug logs export (config.yaml)
file_name = None
encoding = None
file_mode = "a"
if export_logs:
    file_name = os.path.join(project_root, *config["files"]["materialize_logs_path"])
    file_mode = "w"
    encoding = "utf-8"

# Configure logging globally
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=file_name,
    filemode=file_mode,
    encoding=encoding
)

logger = logging.getLogger(__name__)

# Build paths relative to project root
models_dir = os.path.join(project_root, *config["files"]["models_dir"])
marts_dir = os.path.join(project_root, *config["files"]["marts_dir"])
abs_processed_path = os.path.join(project_root, *config["files"]["processed_path"])

# Generate a list of available models
models_list = [f for f in os.listdir(models_dir) if f.endswith('.sql')]

# Create module-level duckdb conncetion
db_connection = duckdb.connect()


def run_model(model_name: str) -> duckdb.DuckDBPyRelation:
    """Executes SQL query on the processed data, mainly for inspection/debugging."""

    model_path = os.path.join(models_dir, model_name)
    
    with open(model_path, 'r') as f:
        query = f.read()
    
    # Replace the template path variable with absolute path
    query = query.format(processed_path=abs_processed_path)

    # Use shared connection
    relation: duckdb.DuckDBPyRelation = db_connection.sql(query)
    
    if logger.isEnabledFor(logging.DEBUG):
        row_count = relation.count('*').fetchone()[0] # type: ignore
        logger.debug(f"Model {model_name}: {row_count} rows")
        logger.debug(f"Preview:\n{relation.limit(5).df()}")

    return relation


def materialize_model(model_name: str, relation: duckdb.DuckDBPyRelation) -> None:
    "Materializes (writes) single relation (table) to parquet."

    # Create model-based file name
    output_file = os.path.join(marts_dir, f"{model_name.replace('.sql', '.parquet')}")
    # Write relation to parquet
    relation.write_parquet(output_file, compression='brotli')


def iterate_materialization() -> None:
    "Iterates materialization process over all models stored in specified 'marts' directory."

    try:  
        logger.info(f"Starting materialization of {len(models_list)} models.")
        for model_name in models_list:
            
            relation = run_model(model_name)
            materialize_model(model_name, relation)
            
            logger.info(f"Completed model: {model_name}")

        # Close connection when all iterations are finished
        db_connection.close()
        logger.info("Materialization successfully completed!")

    except Exception as e:
        logging.critical(f"Materilization failed: {e.__class__.__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    iterate_materialization()
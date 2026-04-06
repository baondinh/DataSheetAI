# tests/test_config.py

from datasheetai.config import AppConfig, DataLoaderConfig

class TestAppConfig: 
    def test_default_config(self): 
        config = AppConfig()
        assert config.logging.level == "DEBUG"
        assert config.data_loader.default_encoding == "utf-8"
        assert config.database.path == "datasheetai.db"
        assert config.schema_manger.include_row_counts == True
        assert config.schema_manger.include_sample_rows == 0

class TestDataLoaderConfig: 
    def test_default_config(self): 
        config = DataLoaderConfig()
        assert config.default_encoding == "utf-8"
        assert config.max_file_size_mb == 100
        assert config.infer_headers == True
        assert config.data_dir == "data"
        assert config.supported_extensions == {
            ".csv": "csv",
            # ".json": "json",
            # ".xlsx": "excel",
        }
        assert config.infer_types == True
        assert config.skip_blank_rows == True
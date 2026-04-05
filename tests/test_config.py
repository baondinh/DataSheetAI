from datasheetai.config import AppConfig, DataLoaderConfig

class TestAppConfig: 
    def test_default_config(self): 
        config = AppConfig()
        assert config.logging.level == "DEBUG"
        assert config.data_loader.default_encoding == "utf-8"
        assert config.database.path == "datasheetai.db"
        assert config.schema_manger.include_row_counts == True
        assert config.schema_manger.include_sample_rows == 0

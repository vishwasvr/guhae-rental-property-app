import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from config import Config

class TestConfig:
    def test_get_aws_config_returns_dict(self):
        config = Config.get_aws_config()
        assert isinstance(config, dict)
        assert 'region' in config
        assert 'dynamodb_table' in config

    def test_is_feature_enabled_true(self):
        # Assuming 'property_image_upload' is a valid feature
        assert Config.is_feature_enabled('property_image_upload') is True

    def test_is_feature_enabled_false(self):
        # Assuming 'non_existent_feature' is not enabled
        assert Config.is_feature_enabled('non_existent_feature') is False

    def test_get_aws_config_missing_key(self):
        config = Config.get_aws_config()
        # Simulate missing key by removing it
        config.pop('region', None)
        assert 'region' not in config

    def test_is_feature_enabled_invalid_type(self):
        with pytest.raises(TypeError):
            Config.is_feature_enabled(None)

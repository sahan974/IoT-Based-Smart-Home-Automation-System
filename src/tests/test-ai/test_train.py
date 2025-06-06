import unittest
from unittest.mock import patch, MagicMock, mock_open
import numpy as np
import pandas as pd
import os
import sys
import tensorflow as tf

# Add the parent directory to sys.path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the functions to test
from ai.train import (
    load_and_preprocess_data,
    prepare_sequences,
    create_lstm_model,
    train_model,
    save_model,
    main
)


class TestTrainFunctions(unittest.TestCase):

    @patch('ai.train.db_get_all_sensor_data')
    def test_load_and_preprocess_data(self, mock_get_data):
        # Mock the return value of db_get_all_sensor_data
        mock_get_data.return_value = {
            'light_sensor1': {
                'category': 'light',
                'data': [
                    (pd.Timestamp('2025-05-01 12:00:00'), 2),
                    (pd.Timestamp('2025-05-01 13:00:00'), 3)
                ]
            },
            'temp_sensor1': {
                'category': 'temp',
                'data': [
                    (pd.Timestamp('2025-05-01 12:00:00'), 22.5),
                    (pd.Timestamp('2025-05-01 13:00:00'), 23.0)
                ]
            }
        }

        # Execute
        data, features, target_features = load_and_preprocess_data()

        # Assert
        self.assertIsInstance(data, np.ndarray)
        self.assertEqual(data.shape[1], 4)  # 2 sensors + hour + day_of_week
        self.assertEqual(len(features), 4)
        self.assertEqual(len(target_features), 2)

    def test_prepare_sequences(self):
        # Create sample data
        features = ['light_sensor1', 'temp_sensor1', 'hour', 'day_of_week']
        target_features = ['light_sensor1', 'temp_sensor1']
        data = np.random.rand(30, 4).astype(np.float32)

        # Execute
        X, y, SEQ_LEN = prepare_sequences(data, features, target_features)

        # Assert
        self.assertEqual(SEQ_LEN, 24)
        self.assertEqual(X.shape, (6, 24, 4))  # 30 - 24 = 6 sequences
        self.assertEqual(y.shape, (6, 2))  # 6 target values, 2 target features

    def test_create_lstm_model(self):
        SEQ_LEN = 24
        features = ['light_sensor1', 'temp_sensor1', 'hour', 'day_of_week']
        target_features = ['light_sensor1', 'temp_sensor1']

        # Execute
        model = create_lstm_model(SEQ_LEN, features, target_features)

        # Assert
        self.assertIsInstance(model, tf.keras.Model)
        self.assertEqual(model.input_shape, (None, SEQ_LEN, len(features)))
        self.assertEqual(model.output_shape, (None, len(target_features)))

    @patch('ai.train.tf.keras.Sequential')
    def test_train_model(self, mock_sequential):
        mock_model = MagicMock()
        mock_sequential.return_value = mock_model

        # Create fake data
        X = np.random.rand(10, 24, 4).astype(np.float32)
        y = np.random.rand(10, 2).astype(np.float32)

        # Execute
        result = train_model(mock_model, X, y)

        # Assert
        mock_model.fit.assert_called_once()
        self.assertEqual(result, mock_model)

    @patch('ai.train.os.path.join')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_model(self, mock_file, mock_join):
        mock_model = MagicMock()
        mock_join.return_value = '/fake/path/model_new.h5'

        # Execute
        save_model(mock_model)

        # Assert
        mock_model.save.assert_called_once_with('/fake/path/model_new.h5')

    @patch('ai.train.load_and_preprocess_data')
    @patch('ai.train.prepare_sequences')
    @patch('ai.train.create_lstm_model')
    @patch('ai.train.train_model')
    @patch('ai.train.save_model')
    def test_main(self, mock_save, mock_train, mock_create, mock_prepare, mock_load):
        # Mock dependencies
        mock_load.return_value = (
            np.random.rand(30, 4),
            ['light_sensor1', 'temp_sensor1', 'hour', 'day_of_week'],
            ['light_sensor1', 'temp_sensor1']
        )
        mock_prepare.return_value = (
            np.random.rand(6, 24, 4),
            np.random.rand(6, 2),
            24
        )
        mock_model = MagicMock()
        mock_create.return_value = mock_model
        mock_train.return_value = mock_model

        # Execute
        main()

        # Assert
        mock_load.assert_called_once()
        mock_prepare.assert_called_once()
        mock_create.assert_called_once()
        mock_train.assert_called_once()
        mock_save.assert_called_once()


if __name__ == '__main__':
    unittest.main()

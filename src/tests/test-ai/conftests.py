"""
This file contains common fixtures and mock data for tests.
"""
import pytest
import numpy as np
import pandas as pd
import datetime
import tensorflow as tf

@pytest.fixture
def mock_sensor_data():
    """
    Return mock sensor data for testing.
    """
    return {
        'living_room_light': {
            'category': 'light',
            'data': [
                (pd.Timestamp('2025-05-01 12:00:00'), 2), 
                (pd.Timestamp('2025-05-01 13:00:00'), 3)
            ]
        },
        'bedroom_light': {
            'category': 'light',
            'data': [
                (pd.Timestamp('2025-05-01 12:00:00'), 1), 
                (pd.Timestamp('2025-05-01 13:00:00'), 0)
            ]
        },
        'living_room_temp': {
            'category': 'temp',
            'data': [
                (pd.Timestamp('2025-05-01 12:00:00'), 22.5), 
                (pd.Timestamp('2025-05-01 13:00:00'), 23.0)
            ]
        },
        'bedroom_temp': {
            'category': 'temp',
            'data': [
                (pd.Timestamp('2025-05-01 12:00:00'), 21.0), 
                (pd.Timestamp('2025-05-01 13:00:00'), 21.5)
            ]
        }
    }

@pytest.fixture
def mock_df_24h():
    """
    Return mock 24-hour sensor DataFrame for testing.
    """
    # Generate 24 hours of timestamps
    timestamps = [
        datetime.datetime(2025, 5, 1, 12, 0) - datetime.timedelta(hours=i) 
        for i in range(24)
    ]
    
    # Create a DataFrame with mock data
    df = pd.DataFrame({
        'timestamp': timestamps,
        'living_room_light': [2] * 24,
        'bedroom_light': [1] * 24,
        'living_room_temp': [22.5] * 24,
        'bedroom_temp': [21.0] * 24,
        'hour': [(12 - i) % 24 for i in range(24)],  # Hour of the day
        'day_of_week': [3] * 24  # 3 represents Wednesday
    })
    
    return df

@pytest.fixture
def mock_test_model():
    """
    Return a simple test TensorFlow model for testing.
    """
    # Define a simple sequential model
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(24, 4)),  # Input shape matches mock data
        tf.keras.layers.LSTM(8, return_sequences=False),  # LSTM layer
        tf.keras.layers.Dense(4)  # Output layer with 4 units
    ])
    
    # Compile the model with Adam optimizer and mean squared error loss
    model.compile(optimizer='adam', loss='mse')
    return model
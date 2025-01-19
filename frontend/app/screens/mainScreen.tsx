import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Animated,
  Dimensions,
  StatusBar,
  TouchableWithoutFeedback,
} from 'react-native';

const SCREEN_HEIGHT = Dimensions.get('window').height;

export default function App() {
  const [activationPhrase, setActivationPhrase] = useState('');
  const [confirmationPhrase, setConfirmationPhrase] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Convert animations to useRef to persist values
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const settingsAnim = useRef(new Animated.Value(SCREEN_HEIGHT)).current;

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopPulseAnimation = () => {
    pulseAnim.setValue(1);
  };

  const toggleSettings = () => {
    Animated.spring(settingsAnim, {
      toValue: isSettingsOpen ? SCREEN_HEIGHT : 0,
      friction: 8,
      tension: 65,
      useNativeDriver: true,
    }).start();
    setIsSettingsOpen(!isSettingsOpen);
  };

  const handleStartCall = async () => {
    if (!activationPhrase || !confirmationPhrase) {
      // Add validation feedback here if needed
      return;
    }
    
    setIsLoading(true);
    startPulseAnimation();
    
    try {
      const response = await fetch('http://<ENTER IP ADDR>:5000/start_call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          activationPhrase,
          confirmationPhrase,
        }),
      });
      const result = await response.json();
      console.log('Server Response:', result);
      
      if (isSettingsOpen) {
        toggleSettings();
      }
    } catch (error) {
      console.error('Error starting call:', error);
      setIsLoading(false);
      stopPulseAnimation();
    }
  };

  const handleEndCall = async () => {
    try {
      const response = await fetch('http://<ENTER IP ADDR>:5000/end_call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const result = await response.json();
      console.log('Server Response:', result);
      setIsLoading(false);
      stopPulseAnimation();
    } catch (error) {
      console.error('Error ending call:', error);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* Main Content */}
      <View style={styles.contentContainer}>
        <Text style={styles.title}>Call Manager</Text>
        
        {/* Active call indicator */}
        {isLoading && (
          <Animated.View 
            style={[
              styles.activeIndicator,
              {
                transform: [{ scale: pulseAnim }],
              },
            ]}
          >
            <Text style={styles.activeText}>Call Active</Text>
          </Animated.View>
        )}

        {/* Settings Button */}
        <TouchableOpacity 
          style={styles.settingsButton} 
          onPress={toggleSettings}
          activeOpacity={0.7}
        >
          <Text style={styles.settingsButtonText}>
            {isSettingsOpen ? 'Close Settings' : 'Settings'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[
            styles.button,
            styles.startButton,
            isLoading && styles.buttonDisabled,
          ]} 
          onPress={handleStartCall}
          disabled={isLoading}
          activeOpacity={0.7}
        >
          <Text style={styles.buttonText}>Start Call</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[
            styles.button,
            styles.endButton,
            !isLoading && styles.buttonDisabled,
          ]} 
          onPress={handleEndCall}
          disabled={!isLoading}
          activeOpacity={0.7}
        >
          <Text style={styles.buttonText}>End Call</Text>
        </TouchableOpacity>
      </View>

      {/* Backdrop */}
      {isSettingsOpen && (
        <TouchableWithoutFeedback onPress={toggleSettings}>
          <View style={styles.backdrop} />
        </TouchableWithoutFeedback>
      )}

      {/* Settings Panel */}
      <Animated.View 
        style={[
          styles.settingsPanel,
          {
            transform: [{ translateY: settingsAnim }],
          },
        ]}
      >
        <View style={styles.settingsPanelContent}>
          <View style={styles.settingsHeader}>
            <Text style={styles.settingsTitle}>Call Settings</Text>
            <View style={styles.dragIndicator} />
          </View>
          <TextInput
            style={styles.input}
            placeholder="Enter Activation Phrase"
            placeholderTextColor="#666"
            value={activationPhrase}
            onChangeText={setActivationPhrase}
          />
          <TextInput
            style={styles.input}
            placeholder="Enter Confirmation Phrase"
            placeholderTextColor="#666"
            value={confirmationPhrase}
            onChangeText={setConfirmationPhrase}
          />
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  contentContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 36,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 40,
    textTransform: 'uppercase',
    letterSpacing: 2,
  },
  button: {
    padding: 18,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    marginVertical: 8,
    elevation: 3,
  },
  startButton: {
    backgroundColor: '#2196F3',
  },
  endButton: {
    backgroundColor: '#F44336',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 1,
  },
  activeIndicator: {
    backgroundColor: '#2196F3',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    marginBottom: 20,
  },
  activeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  settingsButton: {
    backgroundColor: '#333',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginBottom: 20,
  },
  settingsButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  settingsPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#1E1E1E',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -3,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    minHeight: 300,
  },
  settingsPanelContent: {
    paddingBottom: 30,
  },
  settingsHeader: {
    alignItems: 'center',
    marginBottom: 20,
  },
  settingsTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 10,
  },
  dragIndicator: {
    width: 40,
    height: 4,
    backgroundColor: '#666',
    borderRadius: 2,
  },
  input: {
    backgroundColor: '#2A2A2A',
    color: '#fff',
    padding: 18,
    marginBottom: 20,
    borderRadius: 12,
    fontSize: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#333',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
});
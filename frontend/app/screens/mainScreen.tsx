import React, { useState } from 'react';
import { View, Text, TouchableOpacity, TextInput, StyleSheet } from 'react-native';

export default function App() {
  const [activationPhrase, setActivationPhrase] = useState('');
  const [confirmationPhrase, setConfirmationPhrase] = useState('');

  const handleStartCall = async () => {
    try {
      const response = await fetch('http://<ENTER IP ADDR>.115:5000/start_call', {
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
    } catch (error) {
      console.error('Error starting call:', error);
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
    } catch (error) {
      console.error('Error ending call:', error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Call Manager</Text>
      <View style={styles.formContainer}>
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
      <TouchableOpacity style={[styles.button, styles.startButton]} onPress={handleStartCall}>
        <Text style={styles.buttonText}>Start Call</Text>
      </TouchableOpacity>
      <TouchableOpacity style={[styles.button, styles.endButton]} onPress={handleEndCall}>
        <Text style={styles.buttonText}>End Call</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#e3f2fd', // Light blue background
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 30,
  },
  formContainer: {
    width: '100%',
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#fff',
    color: '#333',
    padding: 15,
    marginBottom: 15,
    borderRadius: 20,
    fontSize: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  button: {
    padding: 15,
    borderRadius: 25,
    width: '80%',
    alignItems: 'center',
    marginVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  startButton: {
    backgroundColor: '#4CAF50', // Green for Start
  },
  endButton: {
    backgroundColor: '#F44336', // Red for End
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

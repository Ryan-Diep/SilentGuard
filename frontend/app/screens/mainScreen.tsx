import React, { useState } from 'react';
import { View, Text, TouchableOpacity, TextInput, StyleSheet } from 'react-native';

export default function App() {
  const [activationPhrase, setActivationPhrase] = useState('');
  const [confirmationPhrase, setConfirmationPhrase] = useState('');

  const handleStartCall = async () => {
    try {
      const response = await fetch('http://192.168.50.115:5000/start_call', {
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

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Enter Activation Phrase"
        value={activationPhrase}
        onChangeText={setActivationPhrase}
      />
      <TextInput
        style={styles.input}
        placeholder="Enter Confirmation Phrase"
        value={confirmationPhrase}
        onChangeText={setConfirmationPhrase}
      />
      <TouchableOpacity style={styles.button} onPress={handleStartCall}>
        <Text style={styles.buttonText}>Start Call</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    marginBottom: 20,
    width: '80%',
    borderRadius: 5,
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 20,
    borderRadius: 10,
    width: '80%',
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

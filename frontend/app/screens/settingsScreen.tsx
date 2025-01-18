import React from 'react';
import { View, TextInput, Text, Button, StyleSheet } from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';

type RootStackParamList = {
  Main: undefined;
  Settings: undefined;
};

type SettingsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Settings'>;

type Props = {
  navigation: SettingsScreenNavigationProp;
};

export default function SettingsScreen({ navigation }: Props) {
  const [activationPhrase, setActivationPhrase] = React.useState('');
  const [confirmationPhrase, setConfirmationPhrase] = React.useState('');

  const handleSaveSettings = () => {
    console.log('Activation:', activationPhrase);
    console.log('Confirmation:', confirmationPhrase);
    navigation.goBack(); // Navigate back to the main screen
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Settings</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter Activation Phrase"
        onChangeText={setActivationPhrase}
        value={activationPhrase}
      />
      <TextInput
        style={styles.input}
        placeholder="Enter Confirmation Phrase"
        onChangeText={setConfirmationPhrase}
        value={confirmationPhrase}
      />
      <Button title="Save" onPress={handleSaveSettings} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    fontSize: 24,
    marginBottom: 20,
    fontWeight: 'bold',
  },
  input: {
    height: 50,
    borderColor: '#ccc',
    borderWidth: 1,
    marginBottom: 20,
    paddingLeft: 10,
    borderRadius: 5,
  },
});

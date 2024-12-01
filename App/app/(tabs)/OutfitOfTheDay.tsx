import { StyleSheet, TouchableOpacity } from 'react-native';
import { Text, View } from '@/components/Themed';
import { useNavigation } from '@react-navigation/native';

export default function OutfitOfTheDayScreen() {
  // Get navigation to change header title
  const navigation = useNavigation();

  // Update navigation title to "Outfit of the Day"
  navigation.setOptions({ title: 'Outfit of the Day' });

  return (
    <View style={styles.container}>
      {/* Expanded container for Hat, Top, Bottom, Shoes */}
      <View style={styles.clothingContainer}>
        <View style={styles.box}>
          <Text style={styles.boxText}>Hat</Text>
        </View>
        <View style={styles.box}>
          <Text style={styles.boxText}>Top</Text>
        </View>
        <View style={styles.box}>
          <Text style={styles.boxText}>Bottom</Text>
        </View>
        <View style={styles.box}>
          <Text style={styles.boxText}>Shoes</Text>
        </View>
      </View>

      {/* Separator */}
      <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />

      {/* Buttons for accepting and generating a new outfit, aligned to the bottom */}
      <View style={styles.buttonRow}>
        <TouchableOpacity style={[styles.button, styles.acceptButton]} onPress={() => console.log('Outfit accepted')}>
          <Text style={styles.buttonText}>Accept Outfit</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, styles.generateButton]} onPress={() => console.log('Generate new outfit')}>
          <Text style={styles.buttonText}>Generate New Outfit</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    justifyContent: 'space-between', // Distribute space between clothing boxes and buttons
  },
  clothingContainer: {
    flex: 4, // Allocate more space to clothing items
    justifyContent: 'space-evenly', // Space clothing items evenly
    alignItems: 'center',
  },
  box: {
    width: '80%',
    height: 160, // Increase the height to give it a more prominent presence
    backgroundColor: '#ddd',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 10,
    marginVertical: 5,
  },
  boxText: {
    fontSize: 18,
    fontWeight: '600',
  },
  separator: {
    marginVertical: 20,
    height: 1,
    width: '100%',
    backgroundColor: '#ccc',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 10, // Slight increase in margin for better spacing
    width: '100%',
    alignItems: 'center',
  },
  button: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 10,
    marginHorizontal: 10, // Increase horizontal margin for better spacing between buttons
    alignItems: 'center',
  },
  acceptButton: {
    backgroundColor: '#4CAF50',
  },
  generateButton: {
    backgroundColor: '#4CAF50',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default OutfitOfTheDayScreen;

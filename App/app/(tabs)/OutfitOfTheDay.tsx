import { StyleSheet, TouchableOpacity, Image } from 'react-native';
import { Text, View } from '@/components/Themed';
import { useNavigation } from '@react-navigation/native';
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function OutfitOfTheDay() {
  // Get navigation to change header title
  const navigation = useNavigation();
  const [outfit, setOutfit] = useState([]);
  const userId = 'sloan'; // Example userId; replace with dynamic user ID if needed

  // Update navigation title to "Outfit of the Day"
  useEffect(() => {
    navigation.setOptions({ title: 'Outfit of the Day' });
  }, [navigation]);

  // Function to fetch the outfit of the day from backend
  const fetchOutfit = async (reload = false) => {
    try {
      const response = await axios.get(`http://192.168.72.175:8000/${userId}/outfit_of_the_day`, {
        params: { reload: reload }
      });
      setOutfit(response.data);
    } catch (error) {
      console.error("Failed to fetch outfit of the day:", error);
    }
  };

  // Fetch outfit of the day on component mount
  useEffect(() => {
    fetchOutfit();
  }, []);

  // Handler for generating a new outfit
  const handleGenerateNewOutfit = () => {
    fetchOutfit(true); // Fetch a new outfit with reload=true
  };

  // Handler for accepting the current outfit
  const handleAcceptOutfit = () => {
    console.log('Outfit accepted');
  };

  return (
    <View style={styles.container}>
      {/* Expanded container for Hat, Top, Bottom, Shoes */}
      <View style={styles.clothingContainer}>
        {outfit.map(([id, imagePath], index) => (
          <View key={id} style={styles.box}>
            <Image
              source={{ uri: `http://192.168.72.175:8000/${imagePath}` }}
              style={styles.image}
              resizeMode="cover"
            />
          </View>
        ))}
      </View>

      {/* Buttons for accepting and generating a new outfit, aligned to the bottom */}
      <View style={styles.buttonRow}>
        <TouchableOpacity style={[styles.button, styles.acceptButton]} onPress={handleAcceptOutfit}>
          <Text style={styles.buttonText}>Accept Outfit</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, styles.generateButton]} onPress={handleGenerateNewOutfit}>
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
    justifyContent: 'space-between',
  },
  clothingContainer: {
    flex: 5,
    justifyContent: 'space-evenly',
    alignItems: 'center',
  },
  box: {
    width: '80%',
    flex: 1,
    backgroundColor: '#ddd',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 10,
    marginVertical: 10,
  },
  image: {
    width: '100%',
    height: '100%',
    borderRadius: 10,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    alignItems: 'center',
    marginBottom: 10,
  },
  button: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 10,
    marginHorizontal: 10,
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

export default OutfitOfTheDay;

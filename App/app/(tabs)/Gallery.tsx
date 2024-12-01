import React, { useState, useEffect } from 'react';
import { View, FlatList, StyleSheet, Text, TouchableOpacity, Image, Dimensions } from 'react-native';
import ClothingItem from '../components/ClothingItem'; // Import ClothingItem
import axios from 'axios';

// Get the width of the device's screen
const { width } = Dimensions.get('window');

const Gallery = () => {
  // State to store items fetched from backend
  const [items, setItems] = useState([]);
  const [isModalVisible, setModalVisible] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Load items from the backend
  useEffect(() => {
    const fetchItems = async () => {
      try {
        // Replace with the actual IP address of your laptop
        const response = await axios.get('http://192.168.72.175:8000/sloan/garderobe');
        console.log(response.data);
        setItems(response.data);
      } catch (error) {
        console.error("Failed to fetch items:", error);
      }
    };
    fetchItems();
  }, []);

  const handleImagePress = (index) => {
    // Open the modal and show the selected image
    setSelectedIndex(index);
    setModalVisible(true);
  };

  const handleModalClose = () => {
    setModalVisible(false);
  };

  // Set the number of columns you want
  const numColumns = 3;
  const imageSize = (width - 20) / numColumns - 10; // Calculate image size dynamically

  return (
    <View style={styles.container}>
      <FlatList
        data={items}
        keyExtractor={(item, index) => index.toString()} // Use index to ensure uniqueness
        numColumns={numColumns} // Number of columns for the grid
        renderItem={({ item, index }) => (
          <TouchableOpacity onPress={() => handleImagePress(index)}>
            <View style={[styles.imageContainer, { width: imageSize, height: imageSize }]}>
              <Image source={{ uri: `http://192.168.72.175:8000${item}` }} style={styles.image} />
              <Text style={styles.itemName}>{item}</Text>
            </View>
          </TouchableOpacity>
        )}
      />
      {/* Full-screen modal for displaying images */}
      {isModalVisible && (
        <ClothingItem
          images={items}
          visible={isModalVisible}
          initialIndex={selectedIndex}
          onClose={handleModalClose}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: 10,
    paddingHorizontal: 10,
  },
  header: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  imageContainer: {
    margin: 5,
    borderRadius: 10,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  itemName: {
    marginTop: 5,
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default Gallery;

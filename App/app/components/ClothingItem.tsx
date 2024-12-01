import React from 'react';
import { View, StyleSheet, Image, Dimensions } from 'react-native';
import Modal from 'react-native-modal';
import Swiper from 'react-native-swiper';

const { width, height } = Dimensions.get('window');

const ClothingItem = ({ images, visible, initialIndex, onClose }) => {
    return (
        <Modal
            isVisible={visible}
            style={styles.modal}
            onBackdropPress={onClose}
            swipeDirection={['up']}
            onSwipeComplete={onClose}
            propagateSwipe
        >
            <Swiper
                index={initialIndex}
                loop={false}
                showsPagination={false}
            >
                {images.map((item, index) => (
                    <View key={index} style={styles.imageContainer}>
                        <Image source={{ uri: `http://192.168.72.175:8000/${item}` }} style={styles.fullScreenImage} />
                    </View>
                ))}
            </Swiper>
        </Modal>
    );
};

const styles = StyleSheet.create({
    modal: {
        margin: 0,
    },
    imageContainer: {
        width: width,
        height: height,
        justifyContent: 'center',
        alignItems: 'center',
    },
    fullScreenImage: {
        width: width,
        height: height,
        resizeMode: 'contain',
    },
});

export default ClothingItem;

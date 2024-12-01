import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState, useRef } from 'react';
import { Button, Image, StyleSheet, Text, TouchableOpacity, View, Alert } from 'react-native';
import axios from 'axios';
import Constants from "expo-constants";

export default function Camera() {
    const [facing, setFacing] = useState<CameraType>('back');
    const [permission, requestPermission] = useCameraPermissions();
    const [photoUri, setPhotoUri] = useState<string | null>(null);
    const [userId, setUserId] = useState<string>('123'); // Replace '123' with actual user ID if needed
    const cameraRef = useRef<CameraView | null>(null);

    if (!permission) {
        // Camera permissions are still loading.
        return <View />;
    }

    if (!permission.granted) {
        // Camera permissions are not granted yet.
        return (
            <View style={styles.container}>
                <Text style={styles.message}>We need your permission to show the camera</Text>
                <Button onPress={requestPermission} title="Grant Permission" />
            </View>
        );
    }

    function toggleCameraFacing() {
        setFacing(current => (current === 'back' ? 'front' : 'back'));
    }

    async function takePicture() {
        if (cameraRef.current) {
            const photo = await cameraRef.current.takePictureAsync();
            setPhotoUri(photo.uri); // Store the photo URI
        }
    }

    function retakePicture() {
        setPhotoUri(null); // Reset the photo URI to retake the picture
    }

    async function acceptPicture() {
        if (!photoUri) {
            console.error("No photo to upload");
            return;
        }

        const response = await fetch(photoUri);
        const blob = await response.blob();
        const user_id = 'sloan';
        const formData = new FormData();
        formData.append('file', blob, 'photo.jpg');

        try {
            const response = await axios.post(`http://192.168.72.175:8000/${user_id}/image`, formData, {
                headers: {
                    'Accept': 'application/json', // Optionally, accept JSON
                },
            });

            if (response.status === 200) {
                Alert.alert('Photo uploaded successfully');
            }
        } catch (error) {
            console.error('Upload Error:', error);
            Alert.alert('An error occurred while uploading the photo');
        }
    };

    return (
        <View style={styles.container}>
            {photoUri ? (
                // Render the photo preview with options to accept or retake
                <>
                    <Image source={{ uri: photoUri }} style={styles.preview} />
                    <View style={styles.buttonContainer}>
                        <TouchableOpacity style={styles.acceptButton} onPress={acceptPicture}>
                            <Text style={styles.text}>Accept</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.retakeButton} onPress={retakePicture}>
                            <Text style={styles.text}>Retake</Text>
                        </TouchableOpacity>
                    </View>
                </>
            ) : (
                // Render the camera view with buttons to take a picture
                <>
                    <CameraView style={styles.camera} facing={facing} ref={cameraRef} />
                    <View style={styles.buttonContainer}>
                        <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
                            <Text style={styles.text}>Flip Camera</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                            <Text style={styles.text}>Take Picture</Text>
                        </TouchableOpacity>
                    </View>
                </>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'space-between',
    },
    message: {
        textAlign: 'center',
        paddingBottom: 10,
    },
    camera: {
        flex: 1,
    },
    preview: {
        flex: 1,
        width: '100%',
        height: '100%',
    },
    buttonContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
        padding: 20,
    },
    button: {
        backgroundColor: '#2196F3',
        padding: 10,
        borderRadius: 5,
    },
    captureButton: {
        backgroundColor: '#FF6347',
        padding: 10,
        borderRadius: 5,
    },
    acceptButton: {
        backgroundColor: '#4CAF50',
        padding: 10,
        borderRadius: 5,
    },
    retakeButton: {
        backgroundColor: '#FF6347',
        padding: 10,
        borderRadius: 5,
    },
    text: {
        fontSize: 16,
        fontWeight: 'bold',
        color: 'white',
    },
});

export default Camera;

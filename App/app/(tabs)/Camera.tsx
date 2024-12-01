import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState, useRef } from 'react';
import { Button, Image, StyleSheet, Text, TouchableOpacity, View, Alert } from 'react-native';
import * as FileSystem from 'expo-file-system'; // Import expo-file-system
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
        // console.log(photoUri);
        // console.log(typeof photoUri)
        // // Extract the file name and type
        // const fileName = photoUri.split('/').pop();
        // const fileType = 'image/jpg';  // You can adjust this depending on the type of your image.
        // console.log(fileName);
        // Prepare FormData
        // const formData = new FormData();
        // formData.append('   ', photoUri);
        const user_id = 'obamna';
        const formData = new FormData();
        formData.append('file', blob, 'photo.jpg');
        // formData.append('user_id', user_id);
        const { manifest } = Constants;

        // const uri = `http://${manifest.debuggerHost.split(':').shift()}:8000`;
        // console.log(uri);
        try {
            // const response = await axios.post(`http://192.168.27.175:8000/${user_id}/image`, formData, {
            const response = await axios.post(`http://192.168.72.175:8000/${user_id}/image`, formData, {
                // const response = await axios.post(`http://10.0.2.2:8000/${user_id}/image`, formData, {

                headers: {
                    // 'Content-Type': 'multipart/form-data', // Do NOT set this manually
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



    if (photoUri) {
        // Render the photo preview with options to accept or retake
        return (
            <View style={styles.container}>
                <Image source={{ uri: photoUri }} style={styles.preview} />
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.acceptButton} onPress={acceptPicture}>
                        <Text style={styles.text}>Accept</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.retakeButton} onPress={retakePicture}>
                        <Text style={styles.text}>Retake</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
                        <Text style={styles.text}>Flip Camera</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                        <Text style={styles.text}>Take Picture</Text>
                    </TouchableOpacity>
                </View>
            </CameraView>
        </View>
    );
}

async function convertBlobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            const base64String = reader.result.split(',')[1]; // Extract base64 part
            resolve(base64String);
        };
        reader.onerror = error => reject(error);
    });
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
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
        margin: 20,
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

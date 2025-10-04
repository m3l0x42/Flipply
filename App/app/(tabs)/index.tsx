import { useState, useEffect } from 'react';
import { Button, Image, View, StyleSheet, Alert, ActivityIndicator, Platform, Text } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router'; //

const UPLOAD_URL = 'http://10.253.28.1:8000/analyze-image/';

export default function HomeScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const requestPermissions = async () => {
      await ImagePicker.requestCameraPermissionsAsync();
      if (Platform.OS !== 'web') {
        await ImagePicker.requestMediaLibraryPermissionsAsync();
      }
      setIsReady(true);
    };
    requestPermissions();
  }, []);

  const takeImageHandler = async () => {
    let result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 0.5,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const handleRetake = () => {
    setImageUri(null);
  };
  
  const handleConfirm = () => {
    if (imageUri) {
        uploadImage(imageUri);
    }
  };

  const uploadImage = async (uri: string) => {
    setIsUploading(true);
    const formData = new FormData();
    const fileName = uri.split('/').pop() || 'image.jpg';
    const fileType = fileName.split('.').pop()?.toLowerCase() === 'png' ? 'image/png' : 'image/jpeg';
    formData.append('image', { uri, name: fileName, type: fileType } as any);

    try {
      const response = await fetch(UPLOAD_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Something went wrong on the server!');
      }

      const responseData = await response.json();
      console.log('Upload successful:', responseData);
      
      router.push({
        pathname: "/results",
        params: {
          imageUri: uri,
          analysisData: JSON.stringify(responseData)
        }
      });
      setImageUri(null);

    } catch (error) {
      console.error('Upload failed:', error);
      Alert.alert('Upload Failed', error instanceof Error ? error.message : 'Could not upload the image.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      {isUploading && <ActivityIndicator size="large" color="#0000ff" />}

      {!isUploading && (
        <>
          {imageUri ? (
              <>
            <Image source={{ uri: imageUri }} style={styles.previewImage} />
            <View style={styles.buttonContainer}>
                <Button title="Retake" onPress={handleRetake} color="#ff5c5c" />
                <Button title="Confirm" onPress={handleConfirm} />
            </View>
            </>
          ) : (
            <Button 
              title="Take a Picture" 
              onPress={takeImageHandler} 
              disabled={!isReady} 
            />
          )}
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 20,
    padding: 20,
  },
  previewImage: {
    width: '100%',
    height: '70%',
    resizeMode: 'contain',
    borderRadius: 10,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
});
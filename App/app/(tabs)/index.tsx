import { useState, useEffect } from 'react';
import { Button, Image, View, StyleSheet, Alert, ActivityIndicator, Platform, Text, Pressable } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';


const UPLOAD_URL = 'http://10.253.20.128:8000/analyze-image/';

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

  async function pickFileHandler() {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.5,
      });

      if (!result.canceled) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      console.error('File picking failed:', error);
      Alert.alert('Error', 'Could not pick the file.');
    }
  }

  return (
    <LinearGradient
      colors={['#0d0d0d', '#1a1a1a', '#007AFF']} // fondo negro -> gris oscuro -> azul
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={styles.container}
    >
      {isUploading && <ActivityIndicator size="large" color="#ffffff" />}

      {!isUploading && (
        <>
          {imageUri ? (
            <>
              <Image source={{ uri: imageUri }} style={styles.previewImage} />
              <View style={[styles.buttonContainer, { flexDirection: 'row', justifyContent: 'space-between', gap: 5 }]}>
                <Pressable
                  style={{
                    backgroundColor: '#ff5c5c',
                    paddingVertical: 12,
                    paddingHorizontal: 30,
                    borderRadius: 8,
                    alignItems: 'center',
                  }}
                  onPress={handleRetake}
                >
                  <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 16 }}>
                    Retake
                  </Text>
                </Pressable>

                <Pressable
                  style={{
                    backgroundColor: '#16aa4aff',
                    paddingVertical: 12,
                    paddingHorizontal: 30,
                    borderRadius: 8,
                    alignItems: 'center',
                  }}
                  onPress={handleConfirm}
                >
                  <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 16 }}>
                    Confirm
                  </Text>
                </Pressable>
              </View>
            </>
          ) : (
            <>
              <Pressable
                style={({ pressed }) => [
                  styles.button,
                  pressed && styles.pressedButton,
                ]}
                onPress={takeImageHandler}
                disabled={!isReady}
              >
                <Ionicons name="camera-outline" size={70} color="white" style={{ marginBottom: 5 }} />
                <Text style={{ fontSize: 20, color: 'white', fontWeight: '900', textAlign: 'center' }}>
                  Take a picture
                </Text>
              </Pressable>

              <Pressable
                style={({ pressed }) => [
                  styles.button,
                  pressed && styles.pressedButton,
                ]}
                onPress={pickFileHandler}
                disabled={!isReady}
              >
                <Ionicons name="cloud-upload-outline" size={70} color="white" style={{ marginBottom: 5 }} />
                <Text style={{ fontSize: 20, color: 'white', fontWeight: '900', textAlign: 'center' }}>
                  Upload Files
                </Text>
              </Pressable>
            </>
          )}
        </>
      )}
    </LinearGradient>
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
  // button: {
  //   backgroundColor: '#007AFF',
  //   padding: 40,
  //   borderRadius: 15,
  //   alignItems: 'center',
  //   justifyContent: 'center',
  //   width: 350,
  //   marginVertical: 40,
  // },
  // pressedButton: {
  //   opacity: 0.2,
  // },

  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
    paddingHorizontal: 25,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 25,
    shadowColor: '#ffffffff',
    shadowOffset: { width: 8, height: 3 },
    shadowOpacity: 0.40,
    shadowRadius: 9,
    elevation: 10,
    width: 320,
  },
  pressedButton: {
    opacity: 0.2,
    transform: [{ scale: 0.77 }],
  },
  buttonText: {
    fontSize: 20,
    color: 'white',
    fontWeight: '700',
    textAlign: 'center',
    marginTop: 5,
  },
});
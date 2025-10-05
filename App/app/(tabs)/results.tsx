import { useLocalSearchParams } from 'expo-router';
import { View, Text, Image, StyleSheet, ScrollView, Alert, TouchableOpacity, TextInput } from 'react-native';
import React, { useState, useEffect } from 'react';
import Slider from '@react-native-community/slider';
import { Share } from 'react-native';
import * as WebBrowser from 'expo-web-browser';

type AnalysisResult = {
  brand: string;
  condition: string;
  description: string;
  estimatedPrice: { max: number; min: number; suggested: number };
  item: string;
  searchKeywords: string[];
  imageQuality: 'Excellent' | 'Good' | 'Fair' | 'Poor';
};

export default function ResultsScreen() {
  const params = useLocalSearchParams<{ imageUri: string; analysisData: string }>();

  if (!params.imageUri || !params.analysisData) {
    return <Text>Error: Missing data.</Text>;
  }

  const result: AnalysisResult = JSON.parse(params.analysisData);

  const [itemName, setItemName] = useState(result.item);
  const [brand, setBrand] = useState(result.brand);
  const [description, setDescription] = useState(result.description);
  const [selectedPrice, setSelectedPrice] = useState(result.estimatedPrice.suggested);
  const [loading, setLoading] = useState(false);


  useEffect(() => {
    if (result.imageQuality !== 'Excellent' && result.imageQuality !== 'Good') {
      Alert.alert('Low Image Quality', 'You may want to retake your picture for a better price estimate.');
    }
  }, [result.imageQuality]);

  // Add this line with other useState declarations
  const [condition, setCondition] = useState(result.condition);

  return (
    <View style={styles.screenContainer}>
      <ScrollView contentContainerStyle={styles.scrollContentContainer}>
        <Image source={{ uri: params.imageUri }} style={styles.resultImage} />

        <View style={styles.card}>
          {/* ✅ TextInputs ahora usan estados locales */}
          <TextInput
            style={styles.title}
            value={itemName}
            onChangeText={setItemName}
            placeholder="Item name"
            placeholderTextColor="#888"
            multiline
          />

          <TextInput
            style={styles.brand}
            value={brand}
            onChangeText={setBrand}
            placeholder="Brand"
            placeholderTextColor="#888"
            multiline
          />

          <TextInput
            style={styles.description}
            value={description}
            onChangeText={setDescription}
            placeholder="Description"
            placeholderTextColor="#888"
            multiline
          />

          <View style={styles.separator} />

          <Text style={styles.subHeader}>Condition</Text>
          <TextInput
            style={styles.infoText}
            value={condition}
            onChangeText={setCondition}
            placeholder={result.condition}
            placeholderTextColor="#888"
            multiline
          />

          <Text style={styles.subHeader}>Set Your Price</Text>
          <Text style={styles.priceDisplay}>${selectedPrice.toFixed(2)}</Text>

          <Slider
            style={styles.slider}
            minimumValue={result.estimatedPrice.min}
            maximumValue={result.estimatedPrice.max}
            value={selectedPrice}
            onValueChange={value => setSelectedPrice(value)}
            step={0.05}
            minimumTrackTintColor="#007bff"
            maximumTrackTintColor="#d3d3d3"
            thumbTintColor="#007bff"
          />

          <View style={styles.priceRangeLabels}>
            <Text style={styles.priceRangeText}>${result.estimatedPrice.min.toFixed(2)}</Text>
            <Text style={styles.priceRangeText}>${result.estimatedPrice.max.toFixed(2)}</Text>
          </View>

          <Text style={styles.subHeader}>Search Keywords</Text>
          <Text style={styles.infoText}>{result.searchKeywords.join(', ')}</Text>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.postButton}
          onPress={async () => {
            try {
              setLoading(true);
          
              const formData = new FormData();
              formData.append("title", itemName);
              formData.append("description", description);
              formData.append("price", selectedPrice.toString());
              formData.append("condition", condition);
              formData.append("image", {
                uri: params.imageUri,
                name: "upload.jpg",
                type: "image/jpeg",
              } as any);
          
              const response = await fetch("http://10.253.28.1:8000/post/", {
                method: "POST",
                headers: {
                  "Content-Type": "multipart/form-data",
                },
                body: formData,
              });
          
              if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText);
              }
          
              const data = await response.json();
              Alert.alert("✅ Success", `Listing created: ${data.item_id || "check console"}`);

              Alert.alert("✅ Success", `Listing created!`, [
                {
                  text: "View Listing",
                  onPress: () => WebBrowser.openBrowserAsync(data.listingUrl),
                },
                { text: "OK" }
              ]);

            } catch (error: any) {
              console.error("Error posting listing:", error);
              Alert.alert("❌ Failed to post", error.message || "Unknown error");
            } finally {
              setLoading(false);
            }
          }}          
        >
          <Text style={styles.postButtonText}>Post</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.postButton, { backgroundColor: '#28a745' }]}
          onPress={() => {
            const message = `
📦 ${itemName}
🏷️ Brand: ${brand}
💬 ${description}

💰 Suggested Price: $${selectedPrice.toFixed(2)}
🔎 Keywords: ${result.searchKeywords.join(', ')}

#ForSale #${brand.replace(/\s/g, '')}
`.trim();

            Share.share({
              title: `Share ${itemName}`,
              message,
            });
          }}
        >
          <Text style={styles.postButtonText}>Share</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}


// --- Styles remain the same ---
const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  scrollContentContainer: {
    paddingBottom: 120, // Increased padding to ensure no overlap with footer
  },
  resultImage: {
    width: '100%',
    height: 300,
    resizeMode: 'contain',
    backgroundColor: '#000',
  },
  card: {
    backgroundColor: 'white',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
    borderBottomWidth: 1,
    borderColor: '#eee',
    paddingBottom: 5,
    color: '#000', // Ensure text color is set for TextInput
  },
  brand: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
  separator: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 20,
  },
  subHeader: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 10,
    marginBottom: 5,
  },
  infoText: {
    fontSize: 16,
    color: '#333',
  },
  priceDisplay: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#007bff',
    textAlign: 'center',
    marginVertical: 10,
  },
  slider: {
    width: '100%',
    height: 40,
  },
  priceRangeLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  priceRangeText: {
    fontSize: 12,
    color: '#666',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
    marginBottom: 20,
    paddingHorizontal: 10,
  },
  postButton: {
    flex: 1,
    backgroundColor: '#007bff',
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
  postButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

function setSelectedPrice(suggested: any) {
  throw new Error('Function not implemented.');
}


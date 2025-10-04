import { useLocalSearchParams } from 'expo-router';
import { View, Text, Image, StyleSheet, ScrollView } from 'react-native';

type AnalysisResult = {
  brand: string;
  condition: string;
  description: string;
  estimatedPrice: { max: number; min: number; suggested: number; };
  item: string;
  searchKeywords: string[];
};

export default function ResultsScreen() {
  const params = useLocalSearchParams<{ imageUri: string; analysisData: string }>();
  
  if (!params.imageUri || !params.analysisData) {
    return <Text>Error: Missing data.</Text>;
  }

  const result: AnalysisResult = JSON.parse(params.analysisData);

  return (
    <ScrollView style={styles.container}>
      <Image source={{ uri: params.imageUri }} style={styles.resultImage} />
      
      <View style={styles.card}>
        <Text style={styles.title}>{result.item}</Text>
        <Text style={styles.brand}>Brand: {result.brand}</Text>
        <Text style={styles.description}>{result.description}</Text>
        
        <View style={styles.separator} />
        
        <Text style={styles.subHeader}>Condition</Text>
        <Text style={styles.infoText}>{result.condition}</Text>
        
        <Text style={styles.subHeader}>Estimated Price</Text>
        <Text style={styles.priceText}>
            ${result.estimatedPrice.min.toFixed(2)} - ${result.estimatedPrice.max.toFixed(2)} 
            (Suggested: ${result.estimatedPrice.suggested.toFixed(2)})
        </Text>

        <Text style={styles.subHeader}>Search Keywords</Text>
        <Text style={styles.infoText}>{result.searchKeywords.join(', ')}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
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
  priceText: {
    fontSize: 16,
    color: '#007bff',
    fontWeight: '500',
  },
});
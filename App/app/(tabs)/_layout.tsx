import { Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { View, Text } from 'react-native'; // ✅ added imports

function FlipplyHeaderTitle() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <Ionicons name="mail" size={30} color="blue" />
      <Text style={{ marginLeft: 5, fontSize: 25 }}>  Flipply</Text>
    </View>
  );
}

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{
          headerTitle: () => <FlipplyHeaderTitle />,
          headerStyle: {
            backgroundColor: "grey" // color AppBar
          },
        }}
      />

      <Stack.Screen
        name="results"
        options={{ title: 'Results' }}
      />
    </Stack>
  );
}

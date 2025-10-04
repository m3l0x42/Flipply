import { Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { View, Text } from 'react-native'; // ✅ added imports
import { FontAwesome5 } from '@expo/vector-icons';




function FlipplyHeaderTitle() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <FontAwesome5 name="box" size={30} color='#007AFF' />
      <Text style={{ marginLeft: 5, fontSize: 25, color: "white" }}>  Flipply</Text>
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
            backgroundColor: "rgba(44, 44, 126, 1)" // color AppBar
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

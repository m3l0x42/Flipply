import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: 'Image Upload' }} />
      <Stack.Screen name="results" options={{ title: 'Results' }} />
    </Stack>
  );
}
import React from 'react';
import { StyleSheet, SafeAreaView, StatusBar, Platform } from 'react-native';
import { WebView } from 'react-native-webview';

export default function App() {
  const DJANGO_SERVER_URL = Platform.select({
    web: 'https://cheque-app-7cem.onrender.com',
    default: 'https://cheque-app-7cem.onrender.com',
  });


  if (Platform.OS === 'web') {
    return (
      <div style={{ flex: 1, height: '100vh', width: '100vw', margin: 0, padding: 0, overflow: 'hidden' }}>
        <iframe
          src={DJANGO_SERVER_URL}
          style={{ width: '100%', height: '100%', border: 'none' }}
          title="Cheque System"
        />
      </div>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <WebView
        source={{ uri: DJANGO_SERVER_URL }}
        style={styles.webview}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        scalesPageToFit={true}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  webview: {
    flex: 1,
  },
});

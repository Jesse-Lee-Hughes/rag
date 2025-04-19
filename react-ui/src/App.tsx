import React, { useState, useEffect } from 'react';
import { Box, Container, Grid, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, Paper } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ChatInput } from './components/Chat/ChatInput';
import { ChatMessage } from './components/Chat/ChatMessage';
import { Statistics } from './components/Sidebar/Statistics';
import { SearchResults } from './components/Search/SearchResults';
import { Message, ChatResponse, Statistics as StatsType } from './types';
import * as api from './services/api';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#4791db',
      dark: '#115293',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

const queryClient = new QueryClient();

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<StatsType>({ embedding_count: 0, conversation_count: 0 });
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  const fetchStats = async () => {
    try {
      const newStats = await api.getStatistics();
      setStats(newStats);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSendMessage = async (content: string) => {
    try {
      setLoading(true);
      setMessages((prev) => [...prev, { role: 'user', content }]);

      const response = await api.searchText(content, conversationId);
      setLastResponse(response);
      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, { role: 'assistant', content: response.answer }]);
      
      // Refresh statistics after new message
      fetchStats();
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
          <AppBar position="static" elevation={0}>
            <Toolbar>
              <Typography variant="h6">RAG Assistant</Typography>
            </Toolbar>
          </AppBar>
          <Container maxWidth="xl" sx={{ flexGrow: 1, py: 3 }}>
            <Grid container spacing={3} sx={{ height: '100%' }}>
              <Grid item xs={9}>
                <Paper 
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    height: 'calc(100vh - 140px)',
                    bgcolor: 'background.paper',
                    borderRadius: 2,
                    overflow: 'hidden',
                  }}
                >
                  <Box 
                    sx={{ 
                      flexGrow: 1, 
                      overflow: 'auto', 
                      p: 3,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 2
                    }}
                  >
                    {messages.map((message, index) => (
                      <ChatMessage key={index} message={message} />
                    ))}
                  </Box>
                  <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
                </Paper>
              </Grid>
              <Grid item xs={3}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Statistics stats={stats} />
                  {lastResponse && (
                    <SearchResults
                      sources={lastResponse.sources}
                      sourceLinks={lastResponse.source_links}
                      contextChunks={lastResponse.context_chunks}
                      provider={lastResponse.provider}
                    />
                  )}
                </Box>
              </Grid>
            </Grid>
          </Container>
        </Box>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App; 
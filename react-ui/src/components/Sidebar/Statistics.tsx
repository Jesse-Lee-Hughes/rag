import React from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';
import { Statistics as StatsType } from '../../types';
import StorageIcon from '@mui/icons-material/Storage';
import ChatIcon from '@mui/icons-material/Chat';

interface StatisticsProps {
  stats: StatsType;
}

export const Statistics: React.FC<StatisticsProps> = ({ stats }) => {
  return (
    <Paper sx={{ borderRadius: 2, overflow: 'hidden' }}>
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h6">Statistics</Typography>
      </Box>
      <Box sx={{ p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Box
              sx={{
                p: 2,
                bgcolor: 'grey.50',
                borderRadius: 2,
                textAlign: 'center',
              }}
            >
              <StorageIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="primary" gutterBottom>
                {stats.embedding_count}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                Total Embeddings
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box
              sx={{
                p: 2,
                bgcolor: 'grey.50',
                borderRadius: 2,
                textAlign: 'center',
              }}
            >
              <ChatIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="primary" gutterBottom>
                {stats.conversation_count}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                Total Conversations
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
}; 
import React from 'react';
import { Box, Typography, Paper, Avatar } from '@mui/material';
import { Message } from '../../types';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        gap: 1,
        alignItems: 'flex-start',
      }}
    >
      {!isUser && (
        <Avatar sx={{ bgcolor: 'primary.main' }}>
          <SmartToyIcon />
        </Avatar>
      )}
      <Paper
        sx={{
          p: 2,
          maxWidth: '70%',
          bgcolor: isUser ? 'primary.light' : 'grey.50',
          color: isUser ? 'white' : 'text.primary',
          borderRadius: 2,
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            width: 0,
            height: 0,
            borderStyle: 'solid',
            borderWidth: '8px',
            borderColor: 'transparent',
            top: '10px',
            ...(isUser
              ? {
                  right: '-8px',
                  borderLeftColor: 'primary.light',
                  borderRightWidth: 0,
                }
              : {
                  left: '-8px',
                  borderRightColor: 'grey.50',
                  borderLeftWidth: 0,
                }),
          },
        }}
      >
        <Typography
          variant="body1"
          sx={{
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {message.content}
        </Typography>
      </Paper>
      {isUser && (
        <Avatar sx={{ bgcolor: 'grey.400' }}>
          <PersonIcon />
        </Avatar>
      )}
    </Box>
  );
}; 
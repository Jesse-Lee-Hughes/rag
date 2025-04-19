import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Link,
  Divider,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LinkIcon from '@mui/icons-material/Link';
import DataObjectIcon from '@mui/icons-material/DataObject';
import { SearchResult, SourceLink } from '../../types';

interface SearchResultsProps {
  sources: SearchResult[];
  sourceLinks?: SourceLink[];
  contextChunks?: string[];
  provider?: string;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  sources,
  sourceLinks,
  contextChunks,
  provider,
}) => {
  return (
    <Paper sx={{ borderRadius: 2, overflow: 'hidden' }}>
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h6" gutterBottom>
          Search Results
        </Typography>
        {provider && (
          <Chip
            label={`Provider: ${provider}`}
            size="small"
            sx={{ bgcolor: 'primary.dark', color: 'white' }}
          />
        )}
      </Box>

      {sourceLinks && sourceLinks.length > 0 && (
        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{ bgcolor: 'grey.50' }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LinkIcon color="primary" />
              <Typography>Source Links</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {sourceLinks.map((link, index) => (
                <Box key={index}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    {link.provider}
                  </Typography>
                  <Link
                    href={link.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ wordBreak: 'break-all' }}
                  >
                    {link.link}
                  </Link>
                  {link.metadata && (
                    <Box sx={{ mt: 1 }}>
                      {Object.entries(link.metadata).map(([key, value]) => (
                        <Chip
                          key={key}
                          label={`${key}: ${value}`}
                          size="small"
                          sx={{ mr: 1, mt: 1 }}
                        />
                      ))}
                    </Box>
                  )}
                  {index < sourceLinks.length - 1 && <Divider sx={{ mt: 2 }} />}
                </Box>
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>
      )}

      <Accordion defaultExpanded>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{ bgcolor: 'grey.50' }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DataObjectIcon color="primary" />
            <Typography>Context Information</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {contextChunks?.map((chunk, index) => (
              <Box key={index}>
                <Typography
                  variant="body2"
                  sx={{
                    bgcolor: 'grey.50',
                    p: 2,
                    borderRadius: 1,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {chunk}
                </Typography>
                {sources[index]?.metadata?.similarity_score && (
                  <Chip
                    label={`Relevance: ${(
                      sources[index].metadata.similarity_score * 100
                    ).toFixed(1)}%`}
                    size="small"
                    color="primary"
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
}; 
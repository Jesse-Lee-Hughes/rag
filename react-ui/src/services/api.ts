import axios from 'axios';
import { ChatResponse, Statistics, Conversation } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const searchText = async (
  query_text: string,
  conversation_id?: string,
  memory_window: number = 5
): Promise<ChatResponse> => {
  const response = await api.post('/search/text/', {
    query_text,
    conversation_id,
    memory_window,
  });
  return response.data;
};

export const getStatistics = async (): Promise<Statistics> => {
  const response = await api.get('/admin/table-counts');
  const data = response.data.table_counts;
  return {
    embedding_count: data.find((t: any) => t.table === 'embeddings')?.count || 0,
    conversation_count: (await api.get('/conversations')).data.conversations.length,
  };
};

export const getConversation = async (id: string): Promise<Conversation> => {
  const response = await api.get(`/conversations/${id}`);
  return response.data;
};

export const deleteConversation = async (id: string): Promise<void> => {
  await api.delete(`/conversations/${id}`);
}; 
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input, Button, Typography, Card, Space, Tag, message, AutoComplete } from 'antd';
import { SearchOutlined, QuestionCircleOutlined, FireOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import api from '../services/api';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const HomeContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 60px 20px;
  text-align: center;
`;

const HeroSection = styled.div`
  margin-bottom: 60px;
`;

const SearchSection = styled.div`
  margin-bottom: 50px;
`;

const SearchInput = styled(TextArea)`
  font-size: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  &:focus {
    box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
  }
`;

const SearchButton = styled(Button)`
  height: 50px;
  font-size: 16px;
  border-radius: 25px;
  margin-top: 20px;
  min-width: 120px;
`;

const PopularSection = styled.div`
  margin-bottom: 40px;
`;

const QuestionTag = styled(Tag)`
  margin: 8px;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const StatsSection = styled.div`
  margin-top: 60px;
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatNumber = styled.div`
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 16px;
  opacity: 0.9;
`;

const HomePage = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [popularQuestions, setPopularQuestions] = useState([]);
  const navigate = useNavigate();

  // 预设的热门问题
  const defaultQuestions = [
    "如何提高工作效率？",
    "怎样管理时间？", 
    "如何克服拖延症？",
    "怎么缓解工作压力？",
    "如何建立好习惯？",
    "怎样提升沟通能力？",
    "如何平衡工作和生活？",
    "怎么学会投资理财？"
  ];

  useEffect(() => {
    // 获取热门问题
    loadPopularQuestions();
  }, []);

  const loadPopularQuestions = async () => {
    try {
      const response = await api.get('/search/popular-questions');
      if (response.data && response.data.length > 0) {
        setPopularQuestions(response.data);
      } else {
        // 如果没有数据，使用默认问题
        setPopularQuestions(defaultQuestions.map((q, index) => ({
          question: q,
          search_count: 100 - index * 10,
          category: '个人成长'
        })));
      }
    } catch (error) {
      // 使用默认问题
      setPopularQuestions(defaultQuestions.map((q, index) => ({
        question: q,
        search_count: 100 - index * 10,
        category: '个人成长'
      })));
    }
  };

  const handleSearch = async () => {
    if (!question.trim()) {
      message.warning('请输入你的问题');
      return;
    }

    if (question.length < 5) {
      message.warning('问题太短，请提供更详细的描述');
      return;
    }

    setLoading(true);
    try {
      // 跳转到搜索页面并传递问题
      navigate('/search', { state: { question: question.trim() } });
    } catch (error) {
      message.error('搜索失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionClick = (selectedQuestion) => {
    setQuestion(selectedQuestion);
  };

  const handleSuggestionSearch = async (value) => {
    if (value && value.length >= 2) {
      try {
        const response = await api.get(`/search/suggestions?q=${encodeURIComponent(value)}`);
        setSuggestions(response.data.map(item => ({ value: item })));
      } catch (error) {
        console.log('获取建议失败:', error);
      }
    } else {
      setSuggestions([]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <HomeContainer>
      <HeroSection>
        <Title level={1} style={{ fontSize: '48px', marginBottom: '20px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          🎧 播客解答器
        </Title>
        <Paragraph style={{ fontSize: '20px', color: '#666', marginBottom: '40px' }}>
          有问题，找播客 - 输入你的困扰，我们为你推荐最相关的播客内容
        </Paragraph>
      </HeroSection>

      <SearchSection>
        <AutoComplete
          options={suggestions}
          onSearch={handleSuggestionSearch}
          value={question}
          onChange={setQuestion}
          style={{ width: '100%' }}
        >
          <SearchInput
            placeholder="输入你遇到的问题或困扰...&#10;例如：我最近工作压力很大，总是焦虑，怎么办？"
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            maxLength={500}
          />
        </AutoComplete>
        <div style={{ textAlign: 'right', marginTop: '8px', color: '#999', fontSize: '12px' }}>
          {question.length}/500
        </div>
        <SearchButton
          type="primary"
          icon={<SearchOutlined />}
          loading={loading}
          onClick={handleSearch}
          size="large"
        >
          寻找播客
        </SearchButton>
      </SearchSection>

      <PopularSection>
        <Title level={3} style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <FireOutlined style={{ marginRight: '8px', color: '#ff4d4f' }} />
          热门问题
        </Title>
        <div>
          {popularQuestions.slice(0, 8).map((item, index) => (
            <QuestionTag
              key={index}
              color="blue"
              onClick={() => handleQuestionClick(item.question)}
            >
              {item.question}
            </QuestionTag>
          ))}
        </div>
      </PopularSection>

      <StatsSection>
        <Space size={80}>
          <StatItem>
            <StatNumber>1000+</StatNumber>
            <StatLabel>精选播客</StatLabel>
          </StatItem>
          <StatItem>
            <StatNumber>5000+</StatNumber>
            <StatLabel>播客集数</StatLabel>
          </StatItem>
          <StatItem>
            <StatNumber>50+</StatNumber>
            <StatLabel>话题分类</StatLabel>
          </StatItem>
        </Space>
      </StatsSection>
    </HomeContainer>
  );
};

export default HomePage;
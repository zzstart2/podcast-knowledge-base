import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Typography, 
  Button, 
  Space, 
  Tag, 
  Divider, 
  Alert, 
  Spin,
  Empty,
  Rate,
  message
} from 'antd';
import { 
  PlayCircleOutlined, 
  ClockCircleOutlined, 
  UserOutlined,
  LinkOutlined,
  HeartOutlined,
  ShareAltOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import api from '../services/api';

const { Title, Paragraph, Text } = Typography;

const SearchContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const QuestionCard = styled(Card)`
  margin-bottom: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const ResultCard = styled(Card)`
  margin-bottom: 24px;
  border-radius: 12px;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
`;

const MatchBadge = styled.div`
  position: absolute;
  top: 16px;
  right: 16px;
  background: ${props => {
    if (props.rank === 0) return 'linear-gradient(135deg, #ffd700, #ffed4e)';
    if (props.rank === 1) return 'linear-gradient(135deg, #c0c0c0, #e8e8e8)';
    if (props.rank === 2) return 'linear-gradient(135deg, #cd7f32, #ffa500)';
    return '#f0f0f0';
  }};
  color: ${props => props.rank < 3 ? '#fff' : '#666'};
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const PlatformLinks = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
`;

const PlatformButton = styled(Button)`
  border-radius: 20px;
  font-size: 12px;
`;

const GuestInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
`;

const InsightTag = styled(Tag)`
  margin: 4px;
  border-radius: 12px;
  padding: 4px 12px;
`;

const SearchPage = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  const question = location.state?.question || '';

  useEffect(() => {
    if (question) {
      handleSearch(question);
    } else {
      navigate('/');
    }
  }, [question, navigate]);

  const handleSearch = async (searchQuestion) => {
    setLoading(true);
    try {
      const response = await api.post('/search/', {
        question: searchQuestion
      });

      console.log('搜索结果:', response.data);
      setResults(response.data.recommendations || []);
      setAnalysis(response.data.analysis || null);

      if (response.data.recommendations.length === 0) {
        message.info('没有找到相关播客，试试换个问法吧');
      }
    } catch (error) {
      console.error('搜索失败:', error);
      message.error('搜索失败，请稍后再试');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLinkClick = (url, platform) => {
    // 记录点击事件
    console.log(`点击链接: ${platform} - ${url}`);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const getPlatformIcon = (platform) => {
    const iconMap = {
      'apple_podcasts': '🎵',
      'spotify': '🎧',
      'xiaoyuzhou': '🌌',
      'ximalaya': '📻',
      'default': '🔗'
    };
    return iconMap[platform] || iconMap.default;
  };

  const getRankBadge = (index) => {
    const badges = ['🏆 最匹配', '💡 实用性强', '🔥 用户好评'];
    return badges[index] || `第 ${index + 1} 推荐`;
  };

  const formatDuration = (minutes) => {
    if (!minutes) return '';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}小时${mins}分钟`;
    }
    return `${mins}分钟`;
  };

  if (loading) {
    return (
      <SearchContainer>
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: '20px', fontSize: '16px' }}>
            正在为你搜索最相关的播客...
          </div>
        </div>
      </SearchContainer>
    );
  }

  return (
    <SearchContainer>
      <QuestionCard>
        <Title level={4} style={{ marginBottom: '16px', color: '#1890ff' }}>
          你的问题：
        </Title>
        <Paragraph style={{ fontSize: '16px', margin: 0 }}>
          {question}
        </Paragraph>
      </QuestionCard>

      {analysis && (
        <Alert
          message="AI分析结果"
          description={`问题类型: ${analysis.core_problem || '通用问题'} | 推荐类型: ${analysis.podcast_type || '教育访谈'}`}
          type="info"
          showIcon
          style={{ marginBottom: '24px', borderRadius: '8px' }}
        />
      )}

      {results.length === 0 && !loading ? (
        <Empty
          description="没有找到相关播客"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={() => navigate('/')}>
            重新搜索
          </Button>
        </Empty>
      ) : (
        <>
          <Title level={3} style={{ marginBottom: '24px' }}>
            🎯 为你推荐 {results.length} 期播客：
          </Title>

          {results.map((result, index) => (
            <ResultCard key={result.episode_id} style={{ position: 'relative' }}>
              <MatchBadge rank={index}>
                {getRankBadge(index)}
              </MatchBadge>

              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Title level={4} style={{ marginBottom: '8px', paddingRight: '100px' }}>
                    《{result.podcast_name}》第{result.episode_id}期
                  </Title>
                  <Text strong style={{ fontSize: '16px', color: '#333' }}>
                    💬 {result.title}
                  </Text>
                </div>

                {result.guests && result.guests.length > 0 && (
                  <GuestInfo>
                    <UserOutlined style={{ color: '#1890ff' }} />
                    <Text>
                      嘉宾：{result.guests.map(guest => 
                        `${guest.name}${guest.title ? `（${guest.title}）` : ''}`
                      ).join('、')}
                    </Text>
                  </GuestInfo>
                )}

                <Space size="large">
                  {result.duration_minutes && (
                    <Space>
                      <ClockCircleOutlined />
                      <Text>{formatDuration(result.duration_minutes)}</Text>
                    </Space>
                  )}
                  {result.publish_date && (
                    <Space>
                      📅
                      <Text>{result.publish_date}</Text>
                    </Space>
                  )}
                  {result.quality_score && (
                    <Space>
                      <Rate disabled defaultValue={Math.round(result.quality_score)} />
                      <Text>({result.quality_score.toFixed(1)})</Text>
                    </Space>
                  )}
                </Space>

                {result.content_summary && (
                  <div>
                    <Text strong>📝 内容摘要：</Text>
                    <Paragraph style={{ marginTop: '8px', marginBottom: '0' }}>
                      {result.content_summary}
                    </Paragraph>
                  </div>
                )}

                {result.key_insights && result.key_insights.length > 0 && (
                  <div>
                    <Text strong>💡 核心要点：</Text>
                    <div style={{ marginTop: '8px' }}>
                      {result.key_insights.slice(0, 5).map((insight, idx) => (
                        <InsightTag key={idx} color="blue">
                          {insight}
                        </InsightTag>
                      ))}
                    </div>
                  </div>
                )}

                <Divider style={{ margin: '16px 0' }} />

                <PlatformLinks>
                  {result.links && result.links.length > 0 ? (
                    result.links.map((link, idx) => (
                      <PlatformButton
                        key={idx}
                        icon={<LinkOutlined />}
                        onClick={() => handleLinkClick(link.url, link.platform)}
                      >
                        {getPlatformIcon(link.platform)} {link.platform_name || link.platform}
                      </PlatformButton>
                    ))
                  ) : (
                    <Text type="secondary">暂无播放链接</Text>
                  )}

                  <PlatformButton
                    icon={<HeartOutlined />}
                    style={{ marginLeft: 'auto' }}
                  >
                    收藏
                  </PlatformButton>
                  <PlatformButton
                    icon={<ShareAltOutlined />}
                  >
                    分享
                  </PlatformButton>
                </PlatformLinks>

                {result.match_reason && (
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    匹配原因：{result.match_reason}
                  </Text>
                )}
              </Space>
            </ResultCard>
          ))}
        </>
      )}
    </SearchContainer>
  );
};

export default SearchPage;
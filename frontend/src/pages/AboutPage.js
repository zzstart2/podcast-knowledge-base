import React from 'react';
import { Typography, Card, Space, Divider } from 'antd';
import { HeartOutlined, RocketOutlined, BulbOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const { Title, Paragraph } = Typography;

const AboutContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 60px 20px;
`;

const FeatureCard = styled(Card)`
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  
  .ant-card-body {
    padding: 40px 24px;
  }
  
  .feature-icon {
    font-size: 48px;
    margin-bottom: 20px;
    display: block;
  }
`;

const AboutPage = () => {
  return (
    <AboutContainer>
      <div style={{ textAlign: 'center', marginBottom: '60px' }}>
        <Title level={1}>关于播客解答器</Title>
        <Paragraph style={{ fontSize: '18px', color: '#666' }}>
          让播客成为你问题的答案
        </Paragraph>
      </div>

      <Card style={{ marginBottom: '40px', borderRadius: '12px' }}>
        <Title level={3}>🎯 我们的使命</Title>
        <Paragraph style={{ fontSize: '16px', lineHeight: '1.8' }}>
          在信息爆炸的时代，播客作为深度内容的载体越来越受到人们的喜爱。
          但是面对海量的播客内容，如何快速找到能够解答自己问题的那一期节目，
          成为了许多人的困扰。播客解答器应运而生，我们相信每个问题都有对应的播客答案。
        </Paragraph>
        
        <Paragraph style={{ fontSize: '16px', lineHeight: '1.8' }}>
          我们的目标是建立一个智能的播客推荐系统，让用户只需要输入自己遇到的问题，
          就能获得最相关、最有价值的播客推荐。不再需要漫无目的地搜索，
          不再需要听完整期节目才发现不是自己要找的内容。
        </Paragraph>
      </Card>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={3} style={{ textAlign: 'center' }}>✨ 产品特色</Title>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
          <FeatureCard>
            <BulbOutlined className="feature-icon" style={{ color: '#1890ff' }} />
            <Title level={4}>智能问题分析</Title>
            <Paragraph>
              使用AI技术深度理解你的问题，
              提取关键信息和意图，
              确保推荐的准确性
            </Paragraph>
          </FeatureCard>

          <FeatureCard>
            <RocketOutlined className="feature-icon" style={{ color: '#52c41a' }} />
            <Title level={4}>精准内容匹配</Title>
            <Paragraph>
              多维度搜索算法，
              从标题、内容、嘉宾、话题
              全方位匹配最相关的播客
            </Paragraph>
          </FeatureCard>

          <FeatureCard>
            <HeartOutlined className="feature-icon" style={{ color: '#f5222d' }} />
            <Title level={4}>用户友好体验</Title>
            <Paragraph>
              简洁直观的界面设计，
              清晰的推荐理由，
              多平台播放链接
            </Paragraph>
          </FeatureCard>
        </div>
      </Space>

      <Divider style={{ margin: '60px 0 40px' }} />

      <Card style={{ borderRadius: '12px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={3} style={{ color: 'white', marginBottom: '20px' }}>🚀 开始使用</Title>
          <Paragraph style={{ color: 'white', fontSize: '16px', marginBottom: '0' }}>
            输入你的问题，让我们为你找到最合适的播客内容。
            无论是工作困扰、生活疑问还是学习需求，
            都能在这里找到专业的解答。
          </Paragraph>
        </div>
      </Card>

      <div style={{ textAlign: 'center', marginTop: '40px', color: '#999' }}>
        <Paragraph>
          播客解答器 v1.0.0 | 让知识触手可及
        </Paragraph>
      </div>
    </AboutContainer>
  );
};

export default AboutPage;
import React from 'react';
import { Layout, Menu, Button, Space } from 'antd';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { HomeOutlined, SearchOutlined, InfoCircleOutlined, HeartOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const { Header: AntHeader } = Layout;

const StyledHeader = styled(AntHeader)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const Logo = styled.div`
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-right: 40px;
  cursor: pointer;
`;

const Nav = styled(Menu)`
  border: none;
  flex: 1;
  
  .ant-menu-item {
    border-radius: 8px;
    margin: 0 8px;
    
    &:hover {
      background: rgba(24, 144, 255, 0.1);
    }
  }
  
  .ant-menu-item-selected {
    background: rgba(24, 144, 255, 0.15);
    
    &::after {
      display: none;
    }
  }
`;

const ActionButtons = styled(Space)`
  .ant-btn {
    border-radius: 20px;
    font-weight: 500;
  }
`;

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '搜索',
    },
    {
      key: '/about',
      icon: <InfoCircleOutlined />,
      label: '关于',
    }
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <StyledHeader>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Logo onClick={handleLogoClick}>
          🎧 播客解答器
        </Logo>
        
        <Nav
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </div>

      <ActionButtons>
        <Button 
          type="text" 
          icon={<HeartOutlined />}
          onClick={() => navigate('/favorites')}
        >
          收藏
        </Button>
        
        <Button 
          type="primary" 
          onClick={() => navigate('/search')}
        >
          开始搜索
        </Button>
      </ActionButtons>
    </StyledHeader>
  );
};

export default Header;
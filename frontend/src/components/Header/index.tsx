import { Menu } from "antd";
import {useNavigate} from "react-router-dom";

function AppHeader() {
  const navigate = useNavigate();
  const onMenuClick = (e: any) => {
    console.log("click", e);
    navigate(e.key);
  };
  return (
    <div className="appHeader">
      <Menu mode="horizontal" theme="dark" onClick={onMenuClick}>
        <Menu.Item key="">Home</Menu.Item>
        <Menu.SubMenu key="stats" title="Stats">
          <Menu.Item key="stats/augments">Augments</Menu.Item>
        </Menu.SubMenu>
        <Menu.Item key="players">Players</Menu.Item>
      </Menu>
    </div>
  );
}

export default AppHeader;

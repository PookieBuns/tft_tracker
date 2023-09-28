import Augments from "../Pages/Augments";
import Home from "../Pages/Home";
import { Routes, Route } from "react-router-dom";
import Players from "../Pages/Players";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/stats/augments" element={<Augments />} />
      <Route path="/players" element={<Players />} />
    </Routes>
  );
}

export default AppRoutes;

import Table from "./components/Table";
import { useState, useEffect } from "react";

function App() {
  const [orderBy, setOrderBy] = useState("pick_count");
  const [orderDirection, setOrderDirection] = useState("desc");
  const url = `http://localhost:8000/stats/augments/list?order_by=${orderBy}&order_direction=${orderDirection}`;
  const [data, setData] = useState(null);
  function callAPI() {
    fetch(url)
      .then((response) => response.json())
      .then((data) => setData(data));
    console.log(data);
  }
  useEffect(() => {
    callAPI();
    console.log(data);
  }, []);
  function sort(key: string) {
    setOrderBy(key);
    setOrderDirection(orderDirection === "desc" ? "asc" : "desc");
    callAPI();
  }

  return (
    <>
      <h1>Welcome to the Jankest Augment Stats Page</h1>
      <Table
        rows={data && data["data"] ? data["data"] : []}
        onSort={(key) => sort(key)}
      />
    </>
  );
}

export default App;

import Table from "./components/Table";
import { useState, useEffect, useRef } from "react";

function App() {
  const [orderBy, setOrderBy] = useState("pick_count");
  const [orderDirection, setOrderDirection] = useState("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [data, setData] = useState(null);
  const currentCall = useRef(0);
  function callAPI() {
    let base_url = "http://localhost:8000/stats/augments/list";
    const params: Record<string, string> = {
      order_by: orderBy,
      order_direction: orderDirection,
    };
    if (searchTerm) {
      params.search_term = searchTerm;
    }
    const query_string = new URLSearchParams(params).toString();
    const url = base_url + "?" + query_string;

    currentCall.current = Date.now();
    const thisCall = currentCall.current;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        if (thisCall >= currentCall.current) {
          setData(data);
        }
      });
  }
  useEffect(() => {
    callAPI();
    console.log(data);
  }, [searchTerm, orderBy, orderDirection]);
  function sort(key: string) {
    setOrderBy(key);
    setOrderDirection(orderDirection === "desc" ? "asc" : "desc");
  }
  function search(e: any) {
    setSearchTerm(e.target.value);
  }

  return (
    <>
      <h1>Welcome to the Jankest Augment Stats Page</h1>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => search(e)}
        placeholder="Search"
      ></input>
      <Table
        rows={data && data["data"] ? data["data"] : []}
        onSort={(key) => sort(key)}
      />
    </>
  );
}

export default App;

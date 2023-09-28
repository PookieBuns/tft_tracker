import { Table, Input } from "antd";
import { useEffect, useState, useRef } from "react";
import getStats from "../API";

function Stats() {
  const [orderBy, setOrderBy] = useState("pick_count");
  const [orderDirection, setOrderDirection] = useState("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [columns, setColumns] = useState([]);
  const [rows, setRows] = useState([]);
  const currentCall = useRef(0);
  useEffect(() => {
    currentCall.current = Date.now();
    const callId = currentCall.current;
    getStats(orderBy, orderDirection, searchTerm).then((data) => {
      console.log(data);
      if (data["data"] && callId >= currentCall.current) {
        setColumns(
          Object.keys(data["data"][0]).map((key) => {
            return {
              title: key,
              dataIndex: key,
              key: key,
              sorter: true,
            };
          })
        );
        setRows(data["data"]);
      }
    });
  }, [orderBy, orderDirection, searchTerm]);

  const handleTableChange = (pagination, filters, sorter) => {
    console.log(sorter);
    setOrderBy(sorter.field);
    setOrderDirection(
      sorter.order === "ascend"
        ? "asc"
        : sorter.order === "descend"
        ? "desc"
        : "desc"
    );
  };

  return (
    <>
      <div>
        <Input
          placeholder=""
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <Table
          dataSource={rows}
          columns={columns}
          onChange={handleTableChange}
        />
      </div>
    </>
  );
}

export default Stats;

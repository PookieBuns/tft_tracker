import { ReactNode } from "react";
import { useState } from "react";
interface TableProps {
  rows: { [key: string]: ReactNode }[];
  onSort: (key: string) => void;
}
function Table({ rows, onSort }: TableProps) {
  const headers = rows.length > 0 ? Object.keys(rows[0]) : [];
  return (
    <table className="table">
      <thead>
        <tr>
          {headers.map((header) => (
            <th key={header}>
              {header}
              <button className="btn" onClick={() => onSort(header)}>Sort</button>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {headers.map((header) => (
              <td key={header}>{row[header]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default Table;

import React from "react";
import styles from "./ui.module.css";

interface ProgressProps {
  value: number; // 0 to 100
  className?: string;
}

export function Progress({ value, className = "" }: ProgressProps) {
  const percentage = Math.min(Math.max(value, 0), 100);

  return (
    <div className={`${styles.progressContainer} ${className}`}>
      <div
        className={styles.progressBar}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

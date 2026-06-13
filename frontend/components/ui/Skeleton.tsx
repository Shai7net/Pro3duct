import React from "react";
import styles from "./ui.module.css";

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  circle?: boolean;
  className?: string;
}

export function Skeleton({
  width,
  height,
  circle = false,
  className = "",
}: SkeletonProps) {
  const style: React.CSSProperties = {
    width: width ?? "100%",
    height: height ?? "1rem",
    borderRadius: circle ? "50%" : "var(--border-radius)",
  };

  return (
    <div
      className={`${styles.skeleton} ${className}`}
      style={style}
    />
  );
}

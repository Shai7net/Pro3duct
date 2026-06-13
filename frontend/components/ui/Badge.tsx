import React from "react";
import styles from "./ui.module.css";

interface BadgeProps {
  variant?: "info" | "success" | "warning" | "danger";
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = "info", children, className = "" }: BadgeProps) {
  const classes = [
    styles.badge,
    variant === "info" && styles.badgeInfo,
    variant === "success" && styles.badgeSuccess,
    variant === "warning" && styles.badgeWarning,
    variant === "danger" && styles.badgeDanger,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <span className={classes}>{children}</span>;
}

import Link from "next/link";
import styles from "./page.module.css";

export default function LandingPage() {
  return (
    <div className={styles.landing}>
      <nav className={styles.nav}>
        <div className={styles.logo}><span className={styles.logoIcon}>P3</span><span className={styles.logoText}>Pro3duct</span></div>
        <div className={styles.navLinks}><Link href="/login" className={styles.navLink}>כניסה</Link><Link href="/dashboard" className={styles.navCta}>פתיחת היישום</Link></div>
      </nav>
      <section className={styles.hero}>
        <div className={styles.heroBadge}>יצירת מוצרים אינטראקטיביים בתלת־ממד</div>
        <h1 className={styles.heroTitle}>הופכים תמונות מוצר ל<span className={styles.gradient}> מודל אינטראקטיבי</span></h1>
        <p className={styles.heroSub}>צור פרויקט, העלה תמונות, עקוב אחר תהליך העבודה וערוך את החומרים והאינטראקציות במקום אחד.</p>
        <div className={styles.heroCtas}><Link href="/dashboard" className={styles.ctaPrimary}>כניסה ליישום</Link></div>
      </section>
      <section className={styles.features}>
        <div className={styles.featureCard}><h3>העלאת תמונות פשוטה</h3><p>מעלים מספר תמונות של המוצר מזוויות שונות.</p></div>
        <div className={styles.featureCard}><h3>מעקב ברור</h3><p>רואים בכל רגע מה מצב הפרויקט ומה השלב הבא.</p></div>
        <div className={styles.featureCard}><h3>עורך אינטראקטיבי</h3><p>משנים חומרים, תאורה, לחצנים ומצבי פעולה.</p></div>
      </section>
      <footer className={styles.footer}><span className={styles.footerLogo}>Pro3duct</span><span className={styles.footerText}>סביבת פיתוח מקומית</span></footer>
    </div>
  );
}

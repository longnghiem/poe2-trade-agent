import { footerCls, footerLinkCls } from '../styles'

export function Footer() {
  return (
    <footer className={footerCls}>
      <p>This product isn't affiliated with or endorsed by Grinding Gear Games in any way.</p>
      <p>
        Mod data:{' '}
        <a
          className={footerLinkCls}
          href="https://github.com/Kvan7/Exiled-Exchange-2"
          target="_blank"
          rel="noreferrer"
        >
          Exiled Exchange 2
        </a>{' '}
        (MIT, © 2020 Alexander Drozdov).
      </p>
    </footer>
  )
}

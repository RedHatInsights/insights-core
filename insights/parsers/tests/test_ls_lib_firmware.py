from insights.parsers.ls_lib_firmware import LsLibFW
from insights.tests import context_wrap

LS_LIB_FW = """
/lib/firmware/:
total 53M
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 3com
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 acenic
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 adaptec
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 advansys
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 bnx2
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 bnx2x
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 brcm
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 cis
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 cxgb4
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 dabusb
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 e100
drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 emi26
-rw-r--r--.  1 root root  38K Aug  2  2006 atmel_at76c503-rfmd.bin
-rw-r--r--.  1 root root  35K May  7  2005 atmel_at76c504_2958-wpa.bin
-rw-r--r--.  1 root root 376K May 23  2014 cbfw-3.1.0.0.bin
-rw-r--r--.  1 root root 405K May 23  2014 cbfw-3.2.3.0.bin
lrwxrwxrwx.  1 root root   16 Jul  3 06:53 cbfw.bin -> cbfw-3.0.0.0.bin
lrwxrwxrwx.  1 root root   17 Jul  3 06:53 ct2fw.bin -> ct2fw-3.0.0.0.bin
-rw-r--r--.  1 root root 641K May 24 18:46 ctefx.bin
lrwxrwxrwx.  1 root root   44 Jul 25 07:10 3.10.0-693.35.1.rt56.625.el6rt.x86_64 -> /lib/firmware/3.10.0-693.35.1.rt56.625.el6rt

/lib/firmware/3com:
total 72K
-rw-r--r--. 1 root root 25K May 24 18:46 3C359.bin
-rw-r--r--. 1 root root 44K May 24 18:46 typhoon.bin

/lib/firmware/acenic:
total 148K
-rw-r--r--. 1 root root 72K May 24 18:46 tg1.bin
-rw-r--r--. 1 root root 76K May 24 18:46 tg2.bin

/lib/firmware/adaptec:
total 8.0K
-rw-r--r--. 1 root root 832 May 24 18:46 starfire_rx.bin
-rw-r--r--. 1 root root 832 May 24 18:46 starfire_tx.bin

/lib/firmware/advansys:
total 28K
-rw-r--r--. 1 root root 5.0K May 24 18:46 3550.bin
-rw-r--r--. 1 root root 5.3K May 24 18:46 38C0800.bin

/lib/firmware/bnx2:
total 924K
-rw-r--r--. 1 root root  93K May 24 18:46 bnx2-mips-06-5.0.0.j6.fw
-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.0.15.fw
-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.2.1.fw
-rw-r--r--. 1 root root 7.7K May 24 18:46 bnx2-rv2p-09ax-5.0.0.j10.fw
-rw-r--r--. 1 root root 6.5K May 24 18:46 bnx2-rv2p-09ax-6.0.17.fw

/lib/firmware/bnx2x:
total 8.0M
-rw-r--r--. 1 root root 149K May 24 18:46 bnx2x-e1-6.2.5.0.fw
-rw-r--r--. 1 root root 149K May 24 18:46 bnx2x-e1-6.2.9.0.fw
-rw-r--r--. 1 root root 314K May 24 18:46 bnx2x-e2-7.13.1.0.fw
-rw-r--r--. 1 root root 289K May 24 18:46 bnx2x-e2-7.2.16.0.fw
-rw-r--r--. 1 root root 298K May 24 18:46 bnx2x-e2-7.8.2.0.fw

/lib/firmware/brcm:
total 11M
-rw-r--r--. 1 root root 388K May 24 18:46 brcmfmac43143.bin
-rw-r--r--. 1 root root 538K May 24 18:46 brcmfmac43570-pcie.bin
-rw-r--r--. 1 root root 582K May 24 18:46 brcmfmac43602-pcie.ap.bin
-rw-r--r--. 1 root root  180 May 24 18:46 bcm43xx_hdr-0.fw

/lib/firmware/cis:
total 60K
-rw-r--r--. 1 root root 137 May 24 18:46 3CCFEM556.cis
-rw-r--r--. 1 root root 134 May 24 18:46 3CXEM556.cis
-rw-r--r--. 1 root root 109 May 24 18:46 COMpad2.cis
-rw-r--r--. 1 root root  76 May 24 18:46 COMpad4.cis

/lib/firmware/cpia2:
total 4.0K
-rw-r--r--. 1 root root 824 May 24 18:46 stv0672_vp4.bin

/lib/firmware/cxgb3:
total 116K
-rw-r--r--. 1 root root 1.1K May 24 18:46 ael2005_opt_edc.bin
-rw-r--r--. 1 root root 1.5K May 24 18:46 ael2005_twx_edc.bin
-rw-r--r--. 1 root root 1.6K May 24 18:46 ael2020_twx_edc.bin
-rw-r--r--. 1 root root 2.6K May 24 18:46 t3b_psram-1.1.0.bin

/lib/firmware/cxgb4:
total 4.0M
-rw-r--r--. 1 root root 521K May 24 18:46 t4fw-1.13.32.0.bin
-rw-r--r--. 1 root root 527K May 24 18:46 t4fw-1.14.4.0.bin
-rw-r--r--. 1 root root 529K May 24 18:46 t4fw-1.15.37.0.bin
-rw-r--r--. 1 root root 236K May 24 18:46 t4fw-1.3.10.0.bin

/lib/firmware/dabusb:
total 24K
-rw-r--r--. 1 root root  12K May 24 18:46 bitstream.bin
-rw-r--r--. 1 root root 9.6K May 24 18:46 firmware.fw

/lib/firmware/dsp56k:
total 4.0K
-rw-r--r--. 1 root root 375 May 24 18:46 bootstrap.bin

/lib/firmware/e100:
total 12K
-rw-r--r--. 1 root root 539 May 24 18:46 d101m_ucode.bin
-rw-r--r--. 1 root root 539 May 24 18:46 d101s_ucode.bin
-rw-r--r--. 1 root root 539 May 24 18:46 d102e_ucode.bin

/lib/firmware/edgeport:
total 72K
-rw-r--r--. 1 root root  13K May 24 18:46 down3.bin
-rw-r--r--. 1 root root 6.9K May 24 18:46 boot2.fw
-rw-r--r--. 1 root root 7.1K May 24 18:46 boot.fw
-rw-r--r--. 1 root root  17K May 24 18:46 down2.fw
-rw-r--r--. 1 root root  18K May 24 18:46 down.fw

/lib/firmware/emi26:
total 136K
-rw-r--r--. 1 root root 103K May 24 18:46 bitstream.fw
-rw-r--r--. 1 root root  28K May 24 18:46 firmware.fw
-rw-r--r--. 1 root root 1.9K May 24 18:46 loader.fw

drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 emi26
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 emi62
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 ess
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 kaweth
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 keyspan
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 keyspan_pda
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 korg
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 matrox
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 myricom
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 ositech
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 qlogic
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 r128
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 radeon
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 sb16
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 sun
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 tehuti
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 tigon
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 ttusb-budget
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 vicam
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 yam
drwxr-xr-x. 2 root root 4.0K Jul 25 07:10 yamaha
-rw-r--r--. 1 root root 9.5K Jun 21 17:42 atmsar11.fw
-rw-r--r--. 1 root root  14K Jun 21 17:42 mts_cdma.fw
-rw-r--r--. 1 root root  14K Jun 21 17:42 mts_edge.fw
-rw-r--r--. 1 root root  14K Jun 21 17:42 mts_gsm.fw
-rw-r--r--. 1 root root  14K Jun 21 17:42 ti_3410.fw
-rw-r--r--. 1 root root  14K Jun 21 17:42 ti_5052.fw
-rw-r--r--. 1 root root  24K Jun 21 17:42 whiteheat.fw
-rw-r--r--. 1 root root 5.5K Jun 21 17:42 whiteheat_loader.fw

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/3com:
total 44K
-rw-r--r--. 1 root root 44K Jun 21 17:42 typhoon.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/acenic:
total 148K
-rw-r--r--. 1 root root 72K Jun 21 17:42 tg1.bin
-rw-r--r--. 1 root root 76K Jun 21 17:42 tg2.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/adaptec:
total 8.0K
-rw-r--r--. 1 root root 832 Jun 21 17:42 starfire_rx.bin
-rw-r--r--. 1 root root 832 Jun 21 17:42 starfire_tx.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/advansys:
total 28K
-rw-r--r--. 1 root root 5.0K Jun 21 17:42 3550.bin
-rw-r--r--. 1 root root 5.3K Jun 21 17:42 38C0800.bin
-rw-r--r--. 1 root root 6.2K Jun 21 17:42 38C1600.bin
-rw-r--r--. 1 root root 2.3K Jun 21 17:42 mcode.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/av7110:
total 4.0K
-rw-r--r--. 1 root root 212 Jun 21 17:42 bootcode.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/bnx2:
total 220K
-rw-r--r--. 1 root root  91K Jun 21 17:42 bnx2-mips-06-6.2.1.fw
-rw-r--r--. 1 root root 102K Jun 21 17:42 bnx2-mips-09-6.2.1a.fw
-rw-r--r--. 1 root root 5.6K Jun 21 17:42 bnx2-rv2p-06-6.0.15.fw
-rw-r--r--. 1 root root 6.0K Jun 21 17:42 bnx2-rv2p-09-6.0.17.fw
-rw-r--r--. 1 root root 6.5K Jun 21 17:42 bnx2-rv2p-09ax-6.0.17.fw

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/bnx2x:
total 604K
-rw-r--r--. 1 root root 149K Jun 21 17:42 bnx2x-e1-6.2.9.0.fw
-rw-r--r--. 1 root root 207K Jun 21 17:42 bnx2x-e1h-6.2.9.0.fw
-rw-r--r--. 1 root root 242K Jun 21 17:42 bnx2x-e2-6.2.9.0.fw

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/cis:
total 64K
-rw-r--r--. 1 root root 137 Jun 21 17:42 3CCFEM556.cis
-rw-r--r--. 1 root root 134 Jun 21 17:42 3CXEM556.cis
-rw-r--r--. 1 root root 109 Jun 21 17:42 COMpad2.cis
-rw-r--r--. 1 root root  76 Jun 21 17:42 COMpad4.cis
-rw-r--r--. 1 root root 136 Jun 21 17:42 DP83903.cis
-rw-r--r--. 1 root root 253 Jun 21 17:42 LA-PCM.cis
-rw-r--r--. 1 root root 107 Jun 21 17:42 MT5634ZLX.cis
-rw-r--r--. 1 root root  54 Jun 21 17:42 NE2K.cis
-rw-r--r--. 1 root root 210 Jun 21 17:42 PCMLM28.cis
-rw-r--r--. 1 root root  68 Jun 21 17:42 PE-200.cis
-rw-r--r--. 1 root root  74 Jun 21 17:42 PE520.cis
-rw-r--r--. 1 root root  86 Jun 21 17:42 RS-COM-2P.cis
-rw-r--r--. 1 root root 122 Jun 21 17:42 SW_555_SER.cis
-rw-r--r--. 1 root root 140 Jun 21 17:42 SW_7xx_SER.cis
-rw-r--r--. 1 root root 132 Jun 21 17:42 SW_8xx_SER.cis
-rw-r--r--. 1 root root  85 Jun 21 17:42 tamarack.cis

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/cpia2:
total 4.0K
-rw-r--r--. 1 root root 824 Jun 21 17:42 stv0672_vp4.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/cxgb3:
total 20K
-rw-r--r--. 1 root root 1.1K Jun 21 17:42 ael2005_opt_edc.bin
-rw-r--r--. 1 root root 1.5K Jun 21 17:42 ael2005_twx_edc.bin
-rw-r--r--. 1 root root 1.6K Jun 21 17:42 ael2020_twx_edc.bin
-rw-r--r--. 1 root root 2.6K Jun 21 17:42 t3b_psram-1.1.0.bin
-rw-r--r--. 1 root root 2.6K Jun 21 17:42 t3c_psram-1.1.0.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/dsp56k:
total 4.0K
-rw-r--r--. 1 root root 375 Jun 21 17:42 bootstrap.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/e100:
total 12K
-rw-r--r--. 1 root root 539 Jun 21 17:42 d101m_ucode.bin
-rw-r--r--. 1 root root 539 Jun 21 17:42 d101s_ucode.bin
-rw-r--r--. 1 root root 539 Jun 21 17:42 d102e_ucode.bin

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/edgeport:
total 72K
-rw-r--r--. 1 root root  13K Jun 21 17:42 down3.bin
-rw-r--r--. 1 root root 6.9K Jun 21 17:42 boot2.fw
-rw-r--r--. 1 root root 7.1K Jun 21 17:42 boot.fw
-rw-r--r--. 1 root root  17K Jun 21 17:42 down2.fw
-rw-r--r--. 1 root root  18K Jun 21 17:42 down.fw

/lib/firmware/3.10.0-693.35.1.rt56.625.el6rt/emi26:
total 136K
-rw-r--r--. 1 root root 103K Jun 21 17:42 bitstream.fw
-rw-r--r--. 1 root root  28K Jun 21 17:42 firmware.fw
-rw-r--r--. 1 root root 1.9K Jun 21 17:42 loader.fw
""".strip()


def test_ls_lib_firmware():
    lslib = LsLibFW(context_wrap(LS_LIB_FW))
    assert lslib.data["/lib/firmware/bnx2"]["bnx2-mips-06-6.2.1.fw"] == ['-rw-r--r--.', '1', 'root', 'root', '91K','May', '24', '18:46']
    assert lslib.check_file_present("/lib/firmware/bnx2/bnx2-mips-06-6.2.1.fw") == True
    assert lslib.get_file_details("/lib/firmware/bnx2/bnx2-mips-06-6.2.1.fw") == ['-rw-r--r--.', '1', 'root', 'root', '91K','May', '24', '18:46']

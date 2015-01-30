build_ltp() {
        SrcPath="benchmarks/300.ltp"
   MYPWD=${PWD}
   BuildPATH="$MYPWD/build.ltp"
   TOP_SRCDIR="$MYPWD/$SrcPath"
   INSTALL_DIR="$MYPWD/$OBJPATH"
   mkdir -p $BuildPATH

    if [ $ARCH = "x86_64" -o  $ARCH = "x86_32" ]
        then
            echo $SrcPath
      pushd $BuildPATH
        $TOP_SRCDIR/configure
      eval "make -C $BuildPATH -f $TOP_SRCDIR/Makefile "top_srcdir=$TOP_SRCDIR" "top_builddir=$BuildPATH""
      make -C $BuildPATH -f $TOP_SRCDIR/Makefile "top_srcdir=$TOP_SRCDIR" "top_builddir=$BuildPATH" "DESTDIR=$INSTALL_DIR" SKIP_IDCHECK=1 install
      mv $INSTALL_DIR/opt/ltp  $INSTALL_DIR/ltp
      rm -rf  $INSTALL_DIR/opt
      popd
      rm -rf $BuildPATH
   fi

        if [ $ARCH = "arm_64" -o  $ARCH = "arm_32" ]
        then
                pushd $BuildPATH
                if [ $ARCH = "arm_32" ]; then
                    BUILD="i686-pc-linux-gnu"
                else
                    BUILD="x86_64-unknown-linux-gnu"
                fi
                $TOP_SRCDIR/configure CC=$GCC --target=$ARMCROSS  --host=$ARMCROSS  --build=$BUILD
                make -C $BuildPATH -f $TOP_SRCDIR/Makefile "top_srcdir=$TOP_SRCDIR" "top_builddir=$BuildPATH"
                make -C $BuildPATH -f $TOP_SRCDIR/Makefile "top_srcdir=$TOP_SRCDIR" "top_builddir=$BuildPATH" "DESTDIR=$INSTALL_DIR" SKIP_IDCHECK=1 install
                mv $INSTALL_DIR/opt/ltp  $INSTALL_DIR/ltp
                rm -rf  $INSTALL_DIR/opt
                popd
                rm -rf $BuildPATH
        fi

        if [ $ARCH = "android" ]
        then
                pushd $BuildPATH
      myARMCROSS=arm-linux-gnueabihf
           myGCC=${myARMCROSS}-gcc
                $TOP_SRCDIR/configure CC=$myGCC --target=$myARMCROSS  --host=$myARMCROSS  --build=x86_64-unknown-linux-gnu CFLAGS="-static" LDFLAGS="-static -pthread"
                make -C $BuildPATH -f $TOP_SRCDIR/Makefile "top_srcdir=$TOP_SRCDIR" "top_builddir=$BuildPATH"
                make -C $BuildPATH -f $TOP_SRCDIR/Makefile "top_srcdir=$TOP_SRCDIR" "top_builddir=$BuildPATH" "DESTDIR=$INSTALL_DIR" SKIP_IDCHECK=1 install
                mv $INSTALL_DIR/opt/ltp  $INSTALL_DIR/ltp
                rm -rf  $INSTALL_DIR/opt
                popd
                rm -rf $BuildPATH
        fi
}

build_ltp



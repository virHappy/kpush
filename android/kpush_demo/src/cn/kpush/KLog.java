package cn.kpush;

import android.util.Log;

public class KLog {
    /**
     * 对外static调用
     */
    private static KLog instance = getLogger("kpush");

    public static KLog getLogger(String tag) {
        return new KLog(tag);
    }

    public static void setLevel(int level) {
        instance.setLoggerLevel(level);
    }

    public static void v(String msg){
        instance.verbose(msg);
    }

    public static void d(String msg){
        instance.debug(msg);
    }

    public static void i(String msg){
        instance.info(msg);
    }

    public static void e(String msg){
        instance.error(msg);
    }

    /**
     * log tag
     */
    private String tag = null;//application name
    private int level = Log.ERROR; // 默认级别

    public KLog(String tag) {
        this.tag = tag;
    }

    public void setLoggerLevel(int level) {
        this.level = level;
    }

    /**
     * 获取函数名称
     */
    private String getFunctionName() {
        StackTraceElement[] sts = Thread.currentThread().getStackTrace();

        if (sts == null) {
            return null;
        }

        for (StackTraceElement st : sts) {
            if (st.isNativeMethod()) {
                continue;
            }

            if (st.getClassName().equals(Thread.class.getName())) {
                continue;
            }

            if (st.getClassName().equals(this.getClass().getName())) {
                continue;
            }

            return "[" + Thread.currentThread().getName() + "(" + Thread.currentThread().getId()
                    + ") " + st.getFileName() + ":" + st.getLineNumber() + " " + st.getMethodName() + "]";
        }

        return null;
    }

    private String createMessage(String msg) {
        String functionName = getFunctionName();
        String message = (functionName == null ? msg : (functionName + ": " + msg));
        return message;
    }

    public void verbose(String msg){
        if (Log.VERBOSE < this.level) {
            return;
        }

        String message = createMessage(msg);
        Log.v(tag, message);
    }

    public void debug(String msg){
        if (Log.DEBUG < this.level) {
            return;
        }

        String message = createMessage(msg);
        Log.d(tag, message);
    }

    public void info(String msg){
        if (Log.INFO < this.level) {
            return;
        }

        String message = createMessage(msg);
        Log.i(tag, message);
    }

    public void error(String msg){
        if (Log.ERROR < this.level) {
            return;
        }

        String message = createMessage(msg);
        Log.e(tag, message);
    }
}

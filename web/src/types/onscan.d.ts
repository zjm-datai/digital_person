declare module 'onscan.js' {
    type AttachOptions = {
        onScan?: (code: string, qty?: number) => void;
        onKeyDetect?: (keyCode: number) => void;
        suffixKeyCodes?: number[];
        prefixKeyCodes?: number[];
        reactToPaste?: boolean;
        minLength?: number;
        ignoreIfFocusOn?: string | boolean;
        timeBeforeScanTest?: number;
        avgTimeByChar?: number;
    };

    const api: {
        attachTo(target: Document | HTMLElement, options?: AttachOptions): void;
        detachFrom(target: Document | HTMLElement): void;
    };

    export default api;
}

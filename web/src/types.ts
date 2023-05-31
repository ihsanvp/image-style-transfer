export type E<T> = Event & {
    currentTarget: T;
};
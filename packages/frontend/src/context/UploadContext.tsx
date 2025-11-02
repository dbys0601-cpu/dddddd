import { createContext, ReactNode, useCallback, useContext, useMemo, useReducer } from "react";

import { computeFileSha256 } from "../utils/hash";
import type { FileItem } from "../types";

interface UploadState {
  files: FileItem[];
}

type Action =
  | { type: "ADD_FILES"; payload: FileItem[] }
  | { type: "UPDATE_FILE"; id: string; patch: Partial<FileItem> }
  | { type: "REMOVE_FILE"; id: string }
  | { type: "RESET" };

const initialState: UploadState = {
  files: []
};

function reducer(state: UploadState, action: Action): UploadState {
  switch (action.type) {
    case "ADD_FILES":
      return {
        files: [...state.files, ...action.payload]
      };
    case "UPDATE_FILE":
      return {
        files: state.files.map((file) =>
          file.id === action.id ? { ...file, ...action.patch } : file
        )
      };
    case "REMOVE_FILE":
      return {
        files: state.files.filter((file) => file.id !== action.id)
      };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

interface UploadContextValue {
  files: FileItem[];
  addFiles: (files: File[]) => void;
  removeFile: (id: string) => void;
  updateFile: (id: string, patch: Partial<FileItem>) => void;
  reset: () => void;
}

const UploadContext = createContext<UploadContextValue | undefined>(undefined);

export function UploadProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const addFiles = useCallback(
    (files: File[]) => {
      const validFiles = files.filter((file) => file.size > 0);
      const newItems: FileItem[] = validFiles.map((file) => ({
        id: crypto.randomUUID(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        status: "hashing",
        progress: 0
      }));
      if (!newItems.length) return;
      dispatch({ type: "ADD_FILES", payload: newItems });

      // Compute hashes asynchronously
      newItems.forEach(async (item) => {
        try {
          const sha256 = await computeFileSha256(item.file);
          dispatch({
            type: "UPDATE_FILE",
            id: item.id,
            patch: { sha256, status: "ready", progress: 0 }
          });
        } catch (error) {
          dispatch({
            type: "UPDATE_FILE",
            id: item.id,
            patch: {
              status: "error",
              error: error instanceof Error ? error.message : "Hash hesaplanamad?"
            }
          });
        }
      });
    },
    [dispatch]
  );

  const removeFile = useCallback(
    (id: string) => dispatch({ type: "REMOVE_FILE", id }),
    [dispatch]
  );

  const updateFile = useCallback(
    (id: string, patch: Partial<FileItem>) =>
      dispatch({ type: "UPDATE_FILE", id, patch }),
    [dispatch]
  );

  const reset = useCallback(() => dispatch({ type: "RESET" }), [dispatch]);

  const value = useMemo(
    () => ({ files: state.files, addFiles, removeFile, updateFile, reset }),
    [state.files, addFiles, removeFile, updateFile, reset]
  );

  return <UploadContext.Provider value={value}>{children}</UploadContext.Provider>;
}

export function useUploadContext(): UploadContextValue {
  const ctx = useContext(UploadContext);
  if (!ctx) {
    throw new Error("useUploadContext UploadProvider i?inde kullan?lmal?");
  }
  return ctx;
}


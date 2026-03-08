import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AppRoutes } from "../App";
import { ControlSessionProvider } from "../lib/control-session";

function renderApp(path = "/") {
  return render(
    <ControlSessionProvider>
      <MemoryRouter
        initialEntries={[path]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <AppRoutes />
      </MemoryRouter>
    </ControlSessionProvider>,
  );
}

describe("app shell", () => {
  test("renders required navigation routes", () => {
    renderApp();
    expect(screen.getByRole("navigation", { name: /mission control navigation/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /the floor/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /programs/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /orchestration/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /agent configs/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /state report/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /secrets/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /settings/i })).toBeInTheDocument();
  });

  test("redirects orchestration-center to orchestration", () => {
    renderApp("/orchestration-center");
    expect(screen.getByText("Run Queue And Timeline")).toBeInTheDocument();
  });

  test("keeps operator session keys in memory only", async () => {
    const user = userEvent.setup();
    const setItemSpy = vi.spyOn(Storage.prototype, "setItem");

    renderApp();
    await user.click(screen.getByRole("button", { name: /operator session/i }));
    await user.type(screen.getByPlaceholderText("X-Admin-Key"), "alpha");
    await user.type(screen.getByPlaceholderText("X-Autonomy-Key"), "beta");

    expect(screen.getByText(/frontend session headers are held only in memory/i)).toBeInTheDocument();
    expect(setItemSpy).not.toHaveBeenCalled();

    setItemSpy.mockRestore();
  });
});
